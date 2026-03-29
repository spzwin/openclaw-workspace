// 通知队列 - 持久化通知，防止调度中心宕机丢失

import * as fs from 'fs/promises';
import * as path from 'path';
import { readJson, writeJson, ensureDir, atomicWriteWithVersionCheck } from '../shared/fs-utils';
import { logger } from '../shared/logger';
import { Notification, QueuedNotification, NotificationQueueState } from '../shared/types';

const QUEUE_DIR = 'proj-system/.queue';
const PENDING_DIR = path.join(QUEUE_DIR, 'pending');
const PROCESSING_DIR = path.join(QUEUE_DIR, 'processing');
const COMPLETED_DIR = path.join(QUEUE_DIR, 'completed');
const FAILED_DIR = path.join(QUEUE_DIR, 'failed');
const STATE_PATH = path.join(QUEUE_DIR, 'queue-state.json');

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 5000; // 5 秒

/**
 * 初始化通知队列目录
 */
export async function initQueue(): Promise<void> {
  await ensureDir(PENDING_DIR);
  await ensureDir(PROCESSING_DIR);
  await ensureDir(COMPLETED_DIR);
  await ensureDir(FAILED_DIR);
  logger.info('通知队列目录已初始化');
}

/**
 * 生成唯一队列 ID
 */
function generateQueueId(): string {
  return `notif-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
}

/**
 * 入队通知（原子写入）
 */
export async function enqueueNotification(notification: Notification): Promise<string> {
  await initQueue();
  
  const queued: QueuedNotification = {
    queueId: generateQueueId(),
    notification,
    enqueuedAt: new Date().toISOString(),
    retryCount: 0
  };
  
  const filename = `${Date.now()}-${queued.queueId}.json`;
  const filepath = path.join(PENDING_DIR, filename);
  
  // 原子写入
  await writeJson(filepath, queued);
  logger.info(`通知已入队：${queued.queueId} (项目：${notification.projectId}, 任务：${notification.taskId})`);
  
  return queued.queueId;
}

/**
 * 从队列获取下一个待处理的通知
 */
export async function dequeueNotification(): Promise<QueuedNotification | null> {
  await initQueue();
  
  const files = await fs.readdir(PENDING_DIR);
  if (files.length === 0) {
    return null;
  }
  
  // 按文件名排序（时间戳顺序）
  files.sort();
  
  const firstFile = files[0];
  const filepath = path.join(PENDING_DIR, firstFile);
  
  try {
    const queued = await readJson<QueuedNotification>(filepath);
    
    // 移动到 processing 目录
    const processingPath = path.join(PROCESSING_DIR, firstFile);
    await fs.rename(filepath, processingPath);
    
    logger.debug(`通知已出队：${queued.queueId}`);
    return queued;
  } catch (error: any) {
    logger.error(`读取队列文件失败：${filepath}`, error);
    return null;
  }
}

/**
 * 标记通知处理完成
 */
export async function markNotificationCompleted(queueId: string): Promise<void> {
  const filename = await findNotificationFile(queueId);
  if (!filename) {
    logger.warn(`未找到队列文件：${queueId}`);
    return;
  }
  
  const processingPath = path.join(PROCESSING_DIR, filename);
  const completedPath = path.join(COMPLETED_DIR, filename);
  
  try {
    await fs.rename(processingPath, completedPath);
    logger.debug(`通知标记为完成：${queueId}`);
  } catch (error: any) {
    logger.error(`移动文件失败：${processingPath}`, error);
  }
}

/**
 * 标记通知处理失败（可重试）
 */
export async function markNotificationFailed(
  queueId: string,
  error: string,
  retryable: boolean
): Promise<void> {
  const filename = await findNotificationFile(queueId);
  if (!filename) {
    logger.warn(`未找到队列文件：${queueId}`);
    return;
  }
  
  const processingPath = path.join(PROCESSING_DIR, filename);
  
  try {
    const queued = await readJson<QueuedNotification>(processingPath);
    queued.retryCount++;
    queued.lastAttemptAt = new Date().toISOString();
    queued.error = error;
    
    if (retryable && queued.retryCount < MAX_RETRIES) {
      // 可重试，移回 pending 目录
      const pendingPath = path.join(PENDING_DIR, filename);
      await writeJson(pendingPath, queued);
      await fs.unlink(processingPath);
      logger.warn(`通知处理失败，将重试：${queueId} (第 ${queued.retryCount} 次)`);
    } else {
      // 不可重试或超过最大重试次数，移到 failed 目录
      const failedPath = path.join(FAILED_DIR, filename);
      await writeJson(failedPath, queued);
      await fs.rename(processingPath, failedPath);
      logger.error(`通知处理失败，已放弃：${queueId} (${error})`);
    }
  } catch (error: any) {
    logger.error(`更新队列文件失败：${processingPath}`, error);
  }
}

/**
 * 查找通知文件
 */
async function findNotificationFile(queueId: string): Promise<string | null> {
  for (const dir of [PENDING_DIR, PROCESSING_DIR]) {
    try {
      const files = await fs.readdir(dir);
      for (const file of files) {
        if (file.includes(queueId)) {
          return file;
        }
      }
    } catch {
      // 目录不存在，跳过
    }
  }
  return null;
}

/**
 * 获取队列状态
 */
export async function getQueueState(): Promise<NotificationQueueState> {
  await initQueue();
  
  const [pending, processing, completed, failed] = await Promise.all([
    readQueueDir(PENDING_DIR),
    readQueueDir(PROCESSING_DIR),
    readQueueDir(COMPLETED_DIR),
    readQueueDir(FAILED_DIR)
  ]);
  
  return { pending, processing, completed, failed };
}

/**
 * 读取队列目录
 */
async function readQueueDir(dirPath: string): Promise<QueuedNotification[]> {
  try {
    const files = await fs.readdir(dirPath);
    const notifications: QueuedNotification[] = [];
    
    for (const file of files.slice(0, 100)) { // 限制最多读取 100 条
      try {
        const filepath = path.join(dirPath, file);
        const notif = await readJson<QueuedNotification>(filepath);
        notifications.push(notif);
      } catch {
        // 忽略读取失败的文件
      }
    }
    
    return notifications.sort((a, b) => 
      new Date(a.enqueuedAt).getTime() - new Date(b.enqueuedAt).getTime()
    );
  } catch {
    return [];
  }
}

/**
 * 清理旧的通知文件（保留最近 24 小时）
 * 手动触发或启动时调用，非定时
 */
export async function cleanupOldNotifications(maxAgeHours = 24): Promise<void> {
  await initQueue();
  
  const cutoffTime = Date.now() - (maxAgeHours * 60 * 60 * 1000);
  const dirs = [COMPLETED_DIR, FAILED_DIR];
  let cleanedCount = 0;
  
  for (const dir of dirs) {
    try {
      const files = await fs.readdir(dir);
      for (const file of files) {
        const filepath = path.join(dir, file);
        try {
          const queued = await readJson<QueuedNotification>(filepath);
          const enqueuedAt = new Date(queued.enqueuedAt).getTime();
          
          if (enqueuedAt < cutoffTime) {
            await fs.unlink(filepath);
            cleanedCount++;
          }
        } catch {
          // 忽略读取失败的文件
        }
      }
    } catch (error: any) {
      logger.warn(`清理目录失败：${dir}`, error);
    }
  }
  
  if (cleanedCount > 0) {
    logger.info(`清理完成：${cleanedCount} 个旧通知`);
  }
}

/**
 * 处理队列中的所有通知（调度中心启动时调用）
 */
export async function processQueue(
  processFn: (notification: Notification) => Promise<void>
): Promise<number> {
  let processedCount = 0;
  
  while (true) {
    const queued = await dequeueNotification();
    if (!queued) {
      break;
    }
    
    try {
      await processFn(queued.notification);
      await markNotificationCompleted(queued.queueId);
      processedCount++;
    } catch (error: any) {
      await markNotificationFailed(queued.queueId, error.message, true);
    }
  }
  
  return processedCount;
}
