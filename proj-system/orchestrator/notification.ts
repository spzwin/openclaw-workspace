// 通知处理器 - 处理 Agent 完成通知

import { readJson, writeJson, withFileLock, atomicWriteWithVersionCheck } from '../shared/fs-utils';
import { logger } from '../shared/logger';
import { Notification, NotificationAck, Project, TaskProgress } from '../shared/types';
import { findNextTasks } from './dispatcher';
import { dispatchTaskWithRetry } from './dispatcher';

const PROCESSED_NOTIFICATIONS_PATH = 'proj-system/.processed-notifications.json';
const NOTIFICATION_QUEUE_DIR = 'proj-system/.queue/notifications/';
const MAX_PROCESSED_CACHE = 1000;
const DUPLICATE_WINDOW_MS = 5 * 60 * 1000; // 5 分钟

/**
 * 处理 Agent 完成通知
 */
export async function handleNotification(notification: Notification): Promise<NotificationAck> {
  logger.info(`收到完成通知：${notification.projectId}/${notification.taskId} by ${notification.expertId}`);
  
  // 1. 幂等性检查
  const isDuplicate = await isNotificationProcessed(notification);
  if (isDuplicate) {
    logger.warn(`重复通知，忽略：${notification.id}`);
    return {
      notificationId: notification.id,
      status: 'completed',
      message: '通知已处理（重复）',
      timestamp: new Date().toISOString()
    };
  }
  
  // 2. 验证通知格式
  const validation = validateNotification(notification);
  if (!validation.valid) {
    logger.error(`通知验证失败：${validation.errors.join('; ')}`);
    return {
      notificationId: notification.id,
      status: 'failed',
      message: `验证失败：${validation.errors.join('; ')}`,
      timestamp: new Date().toISOString()
    };
  }
  
  // 3. 发送接收确认
  await sendAck({
    notificationId: notification.id,
    status: 'received',
    timestamp: new Date().toISOString()
  });
  
  try {
    // 4. 更新项目进度（乐观锁）
    const updateSuccess = await updateProjectProgress(notification.projectId, {
      taskId: notification.taskId,
      status: notification.status,
      deliverablePath: notification.deliverablePath,
      completedAt: notification.timestamp,
      completedBy: notification.expertId
    });
    
    if (!updateSuccess) {
      logger.error(`更新项目进度失败：${notification.projectId}`);
      return {
        notificationId: notification.id,
        status: 'failed',
        message: '更新项目进度失败（并发冲突）',
        timestamp: new Date().toISOString()
      };
    }
    
    // 5. 查找下一个任务
    const nextTasks = await findNextTasks(notification.projectId);
    logger.info(`找到 ${nextTasks.length} 个可执行任务`);
    
    // 6. 派发任务（带重试）
    let dispatchedCount = 0;
    for (const task of nextTasks) {
      const result = await dispatchTaskWithRetry(notification.projectId, task);
      
      if (result.success) {
        dispatchedCount++;
      } else {
        logger.error(`任务派发失败：${task.id}`, result.error);
        await handleDispatchFailure(notification.projectId, task, result.error!);
      }
    }
    
    // 7. 标记通知已处理
    await markNotificationProcessed(notification);
    
    // 8. 发送完成确认
    return {
      notificationId: notification.id,
      status: 'completed',
      message: `已派发 ${dispatchedCount} 个新任务`,
      timestamp: new Date().toISOString()
    };
    
  } catch (error: any) {
    logger.error(`处理通知异常：${notification.id}`, error);
    return {
      notificationId: notification.id,
      status: 'failed',
      message: `处理异常：${error.message}`,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * 验证通知格式
 */
function validateNotification(notification: Notification): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // 1. 必填字段检查
  const requiredFields = ['id', 'projectId', 'taskId', 'agentId', 'expertId', 'deliverablePath', 'status', 'timestamp'];
  for (const field of requiredFields) {
    if (!notification[field as keyof Notification]) {
      errors.push(`缺少必填字段：${field}`);
    }
  }
  
  if (errors.length > 0) {
    return { valid: false, errors, warnings };
  }
  
  // 2. 项目编号验证
  const projectPath = `workspace/${notification.projectId}/project.json`;
  // 注意：这里需要实际的 fs 检查
  // if (!fs.existsSync(projectPath)) {
  //   errors.push(`项目不存在：${notification.projectId}`);
  // }
  
  // 3. 成果路径格式验证
  const expectedPathPrefix = `workspace/${notification.projectId}/`;
  if (!notification.deliverablePath.startsWith(expectedPathPrefix)) {
    errors.push(
      `成果路径格式错误：应以 "${expectedPathPrefix}" 开头`
    );
  }
  
  // 4. 状态值验证
  const validStatuses = ['completed', 'failed', 'partial'];
  if (!validStatuses.includes(notification.status)) {
    errors.push(`无效状态：${notification.status}`);
  }
  
  return { valid: errors.length === 0, errors, warnings };
}

/**
 * 更新项目进度（乐观锁）
 */
export async function updateProjectProgress(
  projectId: string,
  taskProgress: TaskProgress,
  maxRetries = 3
): Promise<boolean> {
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const projectPath = `workspace/${projectId}/project.json`;
      const project = await readJson<Project>(projectPath);
      const currentVersion = (project as any).version || 0;
      
      // 应用更新
      if (!project.progress.completedTasks.includes(taskProgress.taskId)) {
        project.progress.completedTasks.push(taskProgress.taskId);
      }
      
      project.progress.pendingTasks = project.progress.pendingTasks.filter(
        id => id !== taskProgress.taskId
      );
      
      // 更新进度百分比
      const totalTasks = project.progress.completedTasks.length + project.progress.pendingTasks.length;
      project.progress.percentComplete = Math.round(
        (project.progress.completedTasks.length / totalTasks) * 100
      );
      
      // 记录交付成果
      if (taskProgress.deliverablePath) {
        project.deliverables.push({
          taskId: taskProgress.taskId,
          path: taskProgress.deliverablePath,
          submittedAt: taskProgress.completedAt,
          submittedBy: taskProgress.completedBy
        });
      }
      
      // 清空当前 Agent
      project.currentAgent = null;
      project.updatedAt = new Date().toISOString();
      
      // 版本号 +1
      (project as any).version = currentVersion + 1;
      
      // 原子写入（带版本检查）
      const success = await atomicWriteWithVersionCheck(
        projectPath,
        project,
        currentVersion
      );
      
      if (success) {
        logger.info(`项目进度已更新：${projectId} v${currentVersion} → v${currentVersion + 1}`);
        return true;
      }
      
      // 版本冲突，重试
      logger.warn(`版本冲突，重试：${projectId}（尝试 ${attempt}/${maxRetries}）`);
      
    } catch (error: any) {
      if (attempt === maxRetries) {
        logger.error(`项目更新失败：${projectId}`, error);
        return false;
      }
    }
  }
  
  return false;
}

/**
 * 检查通知是否已处理（幂等性）
 */
async function isNotificationProcessed(notification: Notification): Promise<boolean> {
  try {
    const processed = await readJson<Record<string, number>>(PROCESSED_NOTIFICATIONS_PATH, {});
    const key = `${notification.projectId}/${notification.taskId}/${notification.expertId}`;
    
    if (processed[key]) {
      const timeSinceLast = Date.now() - processed[key];
      if (timeSinceLast < DUPLICATE_WINDOW_MS) {
        return true; // 5 分钟内的重复
      }
    }
    
    return false;
  } catch {
    return false;
  }
}

/**
 * 标记通知已处理
 */
async function markNotificationProcessed(notification: Notification): Promise<void> {
  try {
    const processed = await readJson<Record<string, number>>(PROCESSED_NOTIFICATIONS_PATH, {});
    const key = `${notification.projectId}/${notification.taskId}/${notification.expertId}`;
    
    processed[key] = Date.now();
    
    // 限制缓存大小
    const keys = Object.keys(processed);
    if (keys.length > MAX_PROCESSED_CACHE) {
      // 删除最旧的一半
      keys.sort((a, b) => processed[a] - processed[b]);
      for (let i = 0; i < keys.length / 2; i++) {
        delete processed[keys[i]];
      }
    }
    
    await writeJson(PROCESSED_NOTIFICATIONS_PATH, processed);
  } catch (error) {
    logger.warn('标记通知已处理失败', error);
  }
}

/**
 * 发送确认
 */
async function sendAck(ack: NotificationAck): Promise<void> {
  // 注意：这里需要实际调用 sessions_send
  logger.info(`发送确认：${ack.notificationId} - ${ack.status}`);
  // await sessions_send({
  //   sessionKey: ack.agentSessionKey || 'default',
  //   message: buildAckMessage(ack)
  // });
}

/**
 * 处理派发失败
 */
async function handleDispatchFailure(
  projectId: string,
  task: any,
  error: string
): Promise<void> {
  logger.error(`任务派发失败，需要人工介入：${projectId}/${task.id}`, error);
  
  // 1. 更新项目状态为 paused
  const projectPath = `workspace/${projectId}/project.json`;
  const project = await readJson<Project>(projectPath);
  project.status = 'paused';
  project.updatedAt = new Date().toISOString();
  await writeJson(projectPath, project);
  
  // 2. 记录失败原因
  logger.warn(`项目已暂停：${projectId}，原因：${error}`);
}
