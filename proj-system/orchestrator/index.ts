// 事件驱动调度中心 - 主入口（纯事件驱动，无定时任务）

import { logger } from '../shared/logger';
import { sessionManager } from './session-manager';
import { initQueue, processQueue, cleanupOldNotifications } from './notification-queue';
import { readProject, updateProjectProgress } from './project-manager';
import { findNextTasks, dispatchTaskWithRetry } from './dispatcher';
import { handleNotification } from './notification-handler';

/**
 * 启动调度中心（纯事件驱动）
 */
export async function startOrchestrator(): Promise<void> {
  logger.info('🚀 启动事件驱动调度中心 v2.2（纯事件驱动）...');
  
  try {
    // 1. 初始化通知队列
    await initQueue();
    logger.info('✓ 通知队列已初始化');
    
    // 2. 启动 Session 管理器（无定时任务）
    await sessionManager.start();
    logger.info('✓ Session 管理器已启动');
    
    // 3. 启动时清理空闲 Session（一次性，非定时）
    await sessionManager.cleanupOnStartup();
    
    // 4. 启动时清理旧通知（一次性，非定时）
    await cleanupOldNotifications(24);
    logger.info('✓ 清理完成');
    
    // 5. 处理未完成的通知（恢复上次宕机时的队列）
    const recoveredCount = await processQueue(handleNotification);
    if (recoveredCount > 0) {
      logger.info(`✓ 恢复 ${recoveredCount} 个未完成的通知`);
    }
    
    // 6. 开始监听新通知（事件驱动）
    startNotificationListener();
    logger.info('✅ 调度中心启动完成，等待通知...');
    
  } catch (error: any) {
    logger.error('调度中心启动失败:', error);
    throw error;
  }
}

/**
 * 启动通知监听器
 * 实际实现需要监听 sessions 或消息队列
 */
function startNotificationListener(): void {
  // 这里需要集成 OpenClaw 的消息监听
  // 伪代码：
  // onMessage(async (message) => {
  //   if (isNotification(message)) {
  //     await handleIncomingNotification(message);
  //   }
  // });
  
  logger.debug('通知监听器运行中...');
}

/**
 * 处理 incoming 通知
 */
export async function handleIncomingNotification(notification: any): Promise<void> {
  try {
    // 1. 入队通知
    await enqueueNotification(notification);
    logger.info(`通知已接收：${notification.projectId}/${notification.taskId}`);
    
    // 2. 立即处理（事件驱动）
    // 或者等待定时任务处理
  } catch (error: any) {
    logger.error(`处理通知失败：${notification?.projectId}/${notification?.taskId}`, error);
  }
}

/**
 * 从队列导入
 */
import { enqueueNotification } from './notification-queue';

// 导出供外部调用
export {
  sessionManager,
  handleNotification,
  findNextTasks,
  dispatchTaskWithRetry,
  updateProjectProgress,
  readProject
};

// 如果是主模块，启动调度中心
if (require.main === module) {
  startOrchestrator().catch(console.error);
}
