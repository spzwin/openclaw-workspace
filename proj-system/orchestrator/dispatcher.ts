// 任务派发器 - 查找并派发下一个任务

import { readJson, writeJson } from '../shared/fs-utils';
import { logger } from '../shared/logger';
import { Pipeline, Task, Project, DispatchResult } from '../shared/types';
import { sessionManager } from './session-manager';

/**
 * 查找下一个可执行的任务
 */
export async function findNextTasks(projectId: string): Promise<Task[]> {
  const project = await readJson<Project>(`workspace/${projectId}/project.json`);
  const pipeline = await readJson<Pipeline>(`workspace/${projectId}/pipeline.json`);
  
  const allTasks = pipeline.phases.flatMap(phase => phase.tasks);
  const nextTasks: Task[] = [];
  
  for (const task of allTasks) {
    // 跳过已完成的任务
    if (project.progress.completedTasks.includes(task.id)) {
      continue;
    }
    
    // 跳过已分配的任务
    if (project.progress.assignedTasks?.includes(task.id)) {
      continue;
    }
    
    // 检查所有依赖是否完成
    const allDepsCompleted = task.dependencies?.every(depId =>
      project.progress.completedTasks.includes(depId)
    ) ?? true;
    
    if (allDepsCompleted) {
      nextTasks.push(task);
    }
  }
  
  return nextTasks;
}

/**
 * 派发任务到 Agent Session（带重试）
 */
export async function dispatchTaskWithRetry(
  projectId: string,
  task: Task,
  maxRetries = 3
): Promise<DispatchResult> {
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // 1. 获取或创建 session
      const session = await sessionManager.getOrCreateSession(task.expertId);
      
      // 2. 收集上游成果
      const upstreamDeliverables = await collectUpstreamDeliverables(projectId, task);
      
      // 3. 构造派单消息
      const message = buildDispatchMessage(projectId, task, upstreamDeliverables);
      
      // 4. 发送消息
      const success = await sessionManager.sendToSession(task.expertId, message);
      
      if (success) {
        // 5. 更新项目状态
        await updateCurrentAgent(projectId, {
          expertId: task.expertId,
          agentId: session.agentId,
          sessionKey: session.sessionKey,
          taskId: task.id,
          assignedAt: new Date().toISOString()
        });
        
        logger.info(`任务派发成功：${task.id} -> ${task.expertId}`);
        return { success: true };
      }
      
      // 发送失败
      logger.warn(`发送失败，重试：${task.id}（尝试 ${attempt}/${maxRetries}）`);
      
    } catch (error: any) {
      logger.error(`任务派发异常（尝试 ${attempt}/${maxRetries}）:`, error);
      
      if (attempt === maxRetries) {
        return {
          success: false,
          error: error.message,
          retryable: isRetryableError(error)
        };
      }
      
      // 指数退避
      await sleep(1000 * Math.pow(2, attempt - 1));
    }
  }
  
  return { success: false, error: '未知错误', retryable: true };
}

/**
 * 收集上游成果
 */
async function collectUpstreamDeliverables(
  projectId: string,
  task: Task
): Promise<string[]> {
  const project = await readJson<Project>(`workspace/${projectId}/project.json`);
  
  const deliverables: string[] = [];
  
  if (task.dependencies) {
    for (const depId of task.dependencies) {
      const deliverable = project.deliverables.find(d => d.taskId === depId);
      if (deliverable) {
        deliverables.push(`- ${depId}: ${deliverable.path}`);
      }
    }
  }
  
  return deliverables;
}

/**
 * 构造派单消息
 */
function buildDispatchMessage(
  projectId: string,
  task: Task,
  upstreamDeliverables: string[]
): string {
  return `【新任务派发】

项目编号：${projectId}
任务 ID：${task.id}
任务名称：${task.name}

上游依赖：
${upstreamDeliverables.length > 0 ? upstreamDeliverables.join('\n') : '无'}

任务描述：
${task.description}

输出要求：
- 路径：workspace/${projectId}/${task.outputPath}
- 格式：可运行的代码 + README

上下文：
- 项目文档：workspace/${projectId}/context/
- 前置成果：workspace/${projectId}/deliverables/

请开始执行，完成后提交通知。`;
}

/**
 * 更新当前 Agent 信息
 */
async function updateCurrentAgent(
  projectId: string,
  agentInfo: {
    expertId: string;
    agentId: string;
    sessionKey: string;
    taskId: string;
    assignedAt: string;
  }
): Promise<void> {
  const projectPath = `workspace/${projectId}/project.json`;
  const project = await readJson<Project>(projectPath);
  
  project.currentAgent = {
    expertId: agentInfo.expertId,
    agentId: agentInfo.agentId,
    sessionKey: agentInfo.sessionKey,
    assignedAt: agentInfo.assignedAt,
    task: agentInfo.taskId
  };
  
  if (!project.progress.assignedTasks) {
    project.progress.assignedTasks = [];
  }
  project.progress.assignedTasks.push(agentInfo.taskId);
  
  project.updatedAt = new Date().toISOString();
  
  await writeJson(projectPath, project);
}

/**
 * 判断错误是否可重试
 */
function isRetryableError(error: any): boolean {
  const retryableMessages = [
    'timeout',
    'network',
    'connection',
    'temporarily unavailable'
  ];
  
  const errorMessage = (error.message || '').toLowerCase();
  return retryableMessages.some(msg => errorMessage.includes(msg));
}

/**
 * 睡眠工具函数
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
