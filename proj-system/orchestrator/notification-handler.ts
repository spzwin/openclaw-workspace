// 通知处理器 - 处理 Agent 提交的任务完成通知

import { logger } from '../shared/logger';
import { Notification, NotificationAck } from '../shared/types';
import { updateProjectProgress } from './project-manager';
import { findNextTasks, dispatchTaskWithRetry } from './dispatcher';
import { sessionManager } from './session-manager';
import { agentCompleteTask } from './agent-status-manager';

/**
 * 处理通知（核心逻辑）
 */
export async function handleNotification(notification: Notification): Promise<void> {
  logger.info(`处理通知：${notification.projectId}/${notification.taskId} by ${notification.expertId}`);
  
  // 1. 验证通知格式
  const validation = validateNotification(notification);
  if (!validation.valid) {
    logger.error(`通知验证失败：${validation.errors.join('; ')}`);
    throw new Error(`通知验证失败：${validation.errors.join('; ')}`);
  }
  
  // 2. 更新项目进度（乐观锁）
  const updateSuccess = await updateProjectProgress(notification.projectId, {
    taskId: notification.taskId,
    status: notification.status,
    deliverablePath: notification.deliverablePath,
    completedAt: notification.timestamp,
    completedBy: notification.expertId
  });
  
  if (!updateSuccess) {
    throw new Error('更新项目进度失败（版本冲突或写入错误）');
  }
  
  // 3. 更新 Agent 状态
  if (notification.status === 'completed') {
    await agentCompleteTask(notification.expertId, notification.deliverablePath, 'completed');
  } else if (notification.status === 'failed') {
    await agentCompleteTask(notification.expertId, notification.deliverablePath, 'failed');
  }
  
  // 4. 查找下一个可执行任务
  const nextTasks = await findNextTasks(notification.projectId);
  logger.info(`找到 ${nextTasks.length} 个可执行任务：${nextTasks.map(t => t.id).join(', ') || '无'}`);
  
  // 5. 派发任务
  for (const task of nextTasks) {
    const result = await dispatchTaskWithRetry(notification.projectId, task);
    
    if (!result.success) {
      logger.error(`任务派发失败：${task.id} -> ${task.expertId}: ${result.error}`);
      // 继续派发其他任务
    }
  }
  
  logger.info(`通知处理完成：${notification.projectId}/${notification.taskId}`);
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
  
  // 必填字段检查
  const requiredFields = ['projectId', 'taskId', 'agentId', 'expertId', 'status', 'deliverablePath', 'timestamp'];
  for (const field of requiredFields) {
    if (!notification[field]) {
      errors.push(`缺少必填字段：${field}`);
    }
  }
  
  if (errors.length > 0) {
    return { valid: false, errors, warnings };
  }
  
  // 状态值验证
  const validStatuses = ['completed', 'failed', 'partial'];
  if (!validStatuses.includes(notification.status)) {
    errors.push(`无效状态：${notification.status}（有效值：${validStatuses.join(', ')}`);
  }
  
  // 成果路径格式验证
  const expectedPathPrefix = `workspace/${notification.projectId}/`;
  if (!notification.deliverablePath.startsWith(expectedPathPrefix)) {
    errors.push(
      `成果路径格式错误：应以 "${expectedPathPrefix}" 开头，实际为 "${notification.deliverablePath}"`
    );
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * 发送通知确认
 */
export async function sendNotificationAck(
  ack: NotificationAck
): Promise<void> {
  // 这里需要调用 sessions_send 发送确认到 Agent
  // 伪代码：
  // await sessions_send({
  //   sessionKey: ack.agentSessionKey,
  //   message: buildAckMessage(ack)
  // });
  
  logger.debug(`发送通知确认：${ack.notificationId} - ${ack.status}`);
}

/**
 * 构建确认消息
 */
function buildAckMessage(ack: NotificationAck): string {
  return `【通知确认】

通知 ID：${ack.notificationId}
状态：${ack.status}
${ack.message ? `消息：${ack.message}` : ''}
时间：${ack.timestamp}`;
}
