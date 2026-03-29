// Session 管理器 - 管理专家 Agent 的 Session 生命周期
// 纯事件驱动：无定时任务，健康检查在发送消息时进行

import { readJson, writeJson, ensureDir } from './fs-utils';
import { logger } from './logger';
import { SessionInfo, SessionRegistry } from '../types';

const REGISTRY_PATH = 'proj-system/.sessions.json';
const MAX_IDLE_TIME = 24 * 60 * 60 * 1000; // 24 小时（仅用于清理建议）

export class SessionManager {
  /**
   * 启动 Session 管理器
   */
  async start() {
    logger.info('启动 Session 管理器（纯事件驱动）...');
    await ensureDir('proj-system');
    
    // 初始化注册表（如果不存在）
    const registry = await this.readRegistry();
    if (!registry) {
      await writeJson(REGISTRY_PATH, {});
      logger.info('Session 注册表已初始化');
    }
    
    // 无定时任务 - 健康检查在发送消息时进行
    logger.info('Session 管理器启动完成');
  }
  
  /**
   * 停止 Session 管理器
   */
  stop() {
    // 无定时器需要清理
  }
  
  /**
   * 获取专家的 Session（复用优先）
   */
  async getSession(expertId: string): Promise<SessionInfo | null> {
    const registry = await this.readRegistry();
    return registry?.[expertId] || null;
  }
  
  /**
   * 获取或创建 Session
   */
  async getOrCreateSession(expertId: string): Promise<SessionInfo> {
    const session = await this.getSession(expertId);
    
    if (session && session.status === 'active') {
      logger.info(`复用现有 Session: ${expertId}`);
      return session;
    }
    
    if (session && session.status === 'error') {
      logger.warn(`Session 异常，重新创建：${expertId}`);
      await this.removeSession(expertId);
    }
    
    // 创建新 Session
    logger.info(`创建新 Session: ${expertId}`);
    return await this.createSession(expertId);
  }
  
  /**
   * 创建新 Session（调用 sessions_spawn）
   */
  private async createSession(expertId: string): Promise<SessionInfo> {
    // 注意：这里需要调用 OpenClaw 的 sessions_spawn API
    // 由于这是 TypeScript 代码，实际实现需要在 Agent 中调用 sessions_spawn
    
    const sessionInfo: SessionInfo = {
      sessionKey: `expert-${expertId}-${Date.now()}`,
      agentId: expertId,
      expertId,
      createdAt: new Date().toISOString(),
      lastUsedAt: new Date().toISOString(),
      status: 'active'
    };
    
    await this.updateSession(sessionInfo);
    return sessionInfo;
  }
  
  /**
   * 更新 Session 信息
   */
  async updateSession(session: SessionInfo): Promise<void> {
    const registry = await this.readRegistry();
    registry[session.expertId] = session;
    await writeJson(REGISTRY_PATH, registry);
  }
  
  /**
   * 移除 Session
   */
  async removeSession(expertId: string): Promise<void> {
    const registry = await this.readRegistry();
    delete registry[expertId];
    await writeJson(REGISTRY_PATH, registry);
  }
  
  /**
   * 发送消息到 Session（事件驱动：发送前检查，失败自动恢复）
   */
  async sendToSession(expertId: string, message: string): Promise<boolean> {
    try {
      const session = await this.getOrCreateSession(expertId);
      
      // 发送前健康检查（仅当 session 存在时）
      if (session.status !== 'active' && session.status !== 'idle') {
        logger.warn(`Session 状态异常，重新创建：${expertId} (${session.status})`);
        await this.removeSession(expertId);
        const newSession = await this.createSession(expertId);
        return await this.doSend(newSession.sessionKey, message);
      }
      
      // 发送消息
      await this.doSend(session.sessionKey, message);
      
      // 更新最后使用时间
      session.lastUsedAt = new Date().toISOString();
      session.status = 'active';
      await this.updateSession(session);
      
      return true;
    } catch (error: any) {
      logger.error(`发送消息失败：${expertId}`, error);
      
      // 标记 Session 为错误状态
      const session = await this.getSession(expertId);
      if (session) {
        session.status = 'error';
        await this.updateSession(session);
      }
      
      return false;
    }
  }
  
  /**
   * 实际发送消息（需要集成 OpenClaw API）
   */
  private async doSend(sessionKey: string, message: string): Promise<void> {
    // 这里需要调用 OpenClaw 的 sessions_send API
    // 伪代码：
    // await sessions_send({ sessionKey, message });
    logger.debug(`发送消息到 ${sessionKey}: ${message.substring(0, 50)}...`);
  }
  
  /**
   * 发送消息前检查 Session 状态（事件驱动：仅在发送时检查）
   */
  private async checkSessionBeforeSend(session: SessionInfo): Promise<boolean> {
    try {
      // 伪代码：发送健康检查消息
      // const response = await sessions_send({
      //   sessionKey: session.sessionKey,
      //   message: '【健康检查】请回复 OK',
      //   timeoutSeconds: 10
      // });
      // return response === 'OK';
      
      // 暂时返回 true，实际实现需要集成 OpenClaw API
      return true;
    } catch (error: any) {
      logger.error(`Session 健康检查失败：${session.expertId}`, error);
      return false;
    }
  }
  
  /**
   * 清理空闲 Session（手动触发或启动时检查，非定时）
   */
  async cleanupIdleSessions() {
    const registry = await this.readRegistry();
    if (!registry) return;
    
    let cleaned = 0;
    const now = Date.now();
    
    for (const [expertId, session] of Object.entries(registry)) {
      const idleTime = now - new Date(session.lastUsedAt).getTime();
      
      if (idleTime > MAX_IDLE_TIME) {
        logger.info(`清理空闲 Session: ${expertId}（空闲 ${idleTime / 1000 / 3600} 小时）`);
        await this.killSession(session.sessionKey);
        delete registry[expertId];
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      await writeJson(REGISTRY_PATH, registry);
      logger.info(`清理完成：${cleaned} 个空闲 Session`);
    }
  }
  
  /**
   * 启动时清理（可选）：启动时检查并清理空闲 Session
   */
  async cleanupOnStartup(): Promise<void> {
    logger.info('检查空闲 Session...');
    await this.cleanupIdleSessions();
  }
  
  /**
   * 杀死 Session
   */
  private async killSession(sessionKey: string): Promise<void> {
    // 伪代码：
    // await sessions_kill({ sessionKey });
    logger.info(`杀死 Session: ${sessionKey}`);
  }
  
  /**
   * 读取注册表
   */
  private async readRegistry(): Promise<SessionRegistry | null> {
    return await readJson<SessionRegistry>(REGISTRY_PATH, null);
  }
}

// 导出单例
export const sessionManager = new SessionManager();
