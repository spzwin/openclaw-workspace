// Agent 状态管理器 - 管理每个 Agent 的个人状态文件

import * as fs from 'fs/promises';
import * as path from 'path';
import { readJson, writeJson, ensureDir } from '../shared/fs-utils';
import { logger } from '../shared/logger';
import { AgentStatus, AgentWorkspaceStatus } from '../shared/types';

const AGENTS_DIR = 'proj-system/agents';

/**
 * 初始化 Agent 目录
 */
export async function initAgentDir(expertId: string): Promise<void> {
  const agentDir = path.join(AGENTS_DIR, expertId);
  await ensureDir(agentDir);
  await ensureDir(path.join(agentDir, 'status'));
}

/**
 * 读取 Agent 状态
 */
export async function readAgentStatus(expertId: string): Promise<AgentStatus | null> {
  const statusPath = path.join(AGENTS_DIR, expertId, 'status.json');
  return await readJson<AgentStatus>(statusPath, null);
}

/**
 * 更新 Agent 状态（个人状态文件）
 */
export async function updateAgentStatus(status: AgentStatus): Promise<void> {
  await initAgentDir(status.expertId);
  
  const statusPath = path.join(AGENTS_DIR, status.expertId, 'status.json');
  status.updatedAt = new Date().toISOString();
  
  await writeJson(statusPath, status);
  logger.debug(`Agent 状态已更新：${status.expertId} - ${status.status}`);
}

/**
 * 创建 Agent 初始状态
 */
export async function createAgentStatus(
  expertId: string,
  agentId: string,
  sessionKey: string,
  capabilities: string[] = []
): Promise<AgentStatus> {
  const now = new Date().toISOString();
  
  const status: AgentStatus = {
    expertId,
    agentId,
    sessionKey,
    currentTask: null,
    taskHistory: [],
    capabilities,
    lastHeartbeat: now,
    status: 'idle',
    updatedAt: now
  };
  
  await updateAgentStatus(status);
  logger.info(`Agent 状态已创建：${expertId}`);
  return status;
}

/**
 * Agent 开始任务
 */
export async function agentStartTask(
  expertId: string,
  projectId: string,
  taskId: string,
  taskName: string
): Promise<void> {
  const status = await readAgentStatus(expertId);
  
  if (!status) {
    logger.error(`Agent 状态不存在：${expertId}`);
    return;
  }
  
  status.currentTask = {
    projectId,
    taskId,
    taskName,
    assignedAt: new Date().toISOString(),
    status: 'working',
    progress: 0,
    lastUpdate: new Date().toISOString()
  };
  
  status.status = 'busy';
  
  await updateAgentStatus(status);
  logger.info(`Agent 开始任务：${expertId} - ${projectId}/${taskId}`);
}

/**
 * Agent 更新任务进度
 */
export async function agentUpdateProgress(
  expertId: string,
  progress: number,
  phase?: string
): Promise<void> {
  const status = await readAgentStatus(expertId);
  
  if (!status || !status.currentTask) {
    return;
  }
  
  status.currentTask.progress = Math.min(100, Math.max(0, progress));
  status.currentTask.lastUpdate = new Date().toISOString();
  
  if (phase) {
    // 可以在这里记录阶段变化
  }
  
  await updateAgentStatus(status);
}

/**
 * Agent 完成任务
 */
export async function agentCompleteTask(
  expertId: string,
  deliverablePath: string,
  statusType: 'completed' | 'failed' | 'partial' = 'completed'
): Promise<void> {
  const status = await readAgentStatus(expertId);
  
  if (!status || !status.currentTask) {
    logger.error(`Agent 没有当前任务：${expertId}`);
    return;
  }
  
  const currentTask = status.currentTask;
  const startedAt = new Date(currentTask.assignedAt).getTime();
  const completedAt = Date.now();
  const durationMinutes = Math.round((completedAt - startedAt) / 60000);
  
  // 添加到历史记录
  status.taskHistory.push({
    projectId: currentTask.projectId,
    taskId: currentTask.taskId,
    taskName: currentTask.taskName,
    status: statusType,
    deliverablePath: statusType === 'completed' ? deliverablePath : undefined,
    startedAt: currentTask.assignedAt,
    completedAt: new Date().toISOString(),
    durationMinutes
  });
  
  // 清空当前任务
  status.currentTask = null;
  status.status = 'idle';
  
  await updateAgentStatus(status);
  logger.info(`Agent 完成任务：${expertId} - ${currentTask.projectId}/${currentTask.taskId} (${durationMinutes}分钟)`);
}

/**
 * Agent 更新工作区状态（项目级别的 agent-status.json）
 */
export async function updateAgentWorkspaceStatus(
  projectId: string,
  expertId: string,
  update: Partial<AgentWorkspaceStatus>
): Promise<void> {
  const workspaceStatusPath = `workspace/${projectId}/${expertId}-status.json`;
  
  let status = await readJson<AgentWorkspaceStatus>(workspaceStatusPath, null);
  
  if (!status) {
    // 创建初始状态
    status = {
      projectId,
      expertId,
      rtDirectory: `${expertId.replace('expert-', 'RT')}_Analysis`,
      phase: 'idle',
      drafts: [],
      research: [],
      deliverables: [],
      log: [],
      updatedAt: new Date().toISOString()
    };
  }
  
  // 应用更新
  Object.assign(status, update);
  status.updatedAt = new Date().toISOString();
  
  // 追加日志
  if (update.phase || update.deliverables?.length) {
    status.log.push({
      timestamp: new Date().toISOString(),
      action: 'status_update',
      details: JSON.stringify(update)
    });
  }
  
  await writeJson(workspaceStatusPath, status);
  logger.debug(`Agent 工作区状态已更新：${projectId}/${expertId}`);
}

/**
 * Agent 心跳
 */
export async function agentHeartbeat(expertId: string): Promise<void> {
  const status = await readAgentStatus(expertId);
  
  if (!status) {
    return;
  }
  
  status.lastHeartbeat = new Date().toISOString();
  
  // 如果离线但有 session，恢复为 idle
  if (status.status === 'offline' && status.sessionKey) {
    status.status = 'idle';
  }
  
  await updateAgentStatus(status);
}

/**
 * 标记 Agent 离线
 */
export async function markAgentOffline(expertId: string, errorMessage?: string): Promise<void> {
  const status = await readAgentStatus(expertId);
  
  if (!status) {
    return;
  }
  
  status.status = 'offline';
  status.errorMessage = errorMessage;
  status.updatedAt = new Date().toISOString();
  
  await updateAgentStatus(status);
  logger.warn(`Agent 已标记为离线：${expertId}${errorMessage ? ` - ${errorMessage}` : ''}`);
}

/**
 * 获取所有 Agent 状态
 */
export async function getAllAgentStatuses(): Promise<AgentStatus[]> {
  try {
    const agentsDir = await fs.readdir(AGENTS_DIR);
    const statuses: AgentStatus[] = [];
    
    for (const expertId of agentsDir) {
      const status = await readAgentStatus(expertId);
      if (status) {
        statuses.push(status);
      }
    }
    
    return statuses;
  } catch {
    return [];
  }
}
