// 项目管理器 - 乐观锁更新项目进度

import { readJson, writeJson, atomicWriteWithVersionCheck } from '../shared/fs-utils';
import { logger } from '../shared/logger';
import { Project, TaskProgress, Notification } from '../shared/types';

const MAX_RETRIES = 3;

/**
 * 读取项目信息
 */
export async function readProject(projectId: string): Promise<Project> {
  const projectPath = `workspace/${projectId}/meta.json`;
  return await readJson<Project>(projectPath);
}

/**
 * 更新项目进度（乐观锁）
 */
export async function updateProjectProgress(
  projectId: string,
  progressUpdate: TaskProgress,
  maxRetries = MAX_RETRIES
): Promise<boolean> {
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const projectPath = `workspace/${projectId}/meta.json`;
      
      // 1. 读取当前版本
      const project = await readJson<Project>(projectPath);
      const currentVersion = project.version;
      
      // 2. 应用更新
      const updatedProject = applyProgressUpdate(project, progressUpdate);
      updatedProject.version = currentVersion + 1;
      updatedProject.updatedAt = new Date().toISOString();
      
      // 3. 原子写入（带版本检查）
      const success = await atomicWriteWithVersionCheck(projectPath, updatedProject, currentVersion);
      
      if (success) {
        logger.info(`项目进度更新成功：${projectId} v${currentVersion} → v${currentVersion + 1}`);
        
        // 4. 追加历史日志
        await appendHistoryLog(projectId, {
          timestamp: new Date().toISOString(),
          action: 'task_completed',
          taskId: progressUpdate.taskId,
          status: progressUpdate.status,
          completedBy: progressUpdate.completedBy
        });
        
        return true;
      }
      
      // 版本冲突，重试
      logger.warn(`版本冲突，重试：${projectId}（尝试 ${attempt}/${maxRetries}）`);
      await sleep(100 * attempt);
      
    } catch (error: any) {
      logger.error(`项目更新失败：${projectId}（尝试 ${attempt}/${maxRetries}）`, error);
      
      if (attempt === maxRetries) {
        return false;
      }
      
      await sleep(100 * attempt);
    }
  }
  
  return false;
}

/**
 * 应用进度更新
 */
function applyProgressUpdate(project: Project, update: TaskProgress): Project {
  // 标记任务完成
  if (!project.progress.completedTasks.includes(update.taskId)) {
    project.progress.completedTasks.push(update.taskId);
  }
  
  // 从待处理任务中移除
  project.progress.pendingTasks = project.progress.pendingTasks.filter(
    id => id !== update.taskId
  );
  
  // 从已分配任务中移除
  if (project.progress.assignedTasks) {
    project.progress.assignedTasks = project.progress.assignedTasks.filter(
      id => id !== update.taskId
    );
  }
  
  // 更新完成百分比
  const pipelineTotalTasks = project.progress.completedTasks.length + 
                             project.progress.pendingTasks.length + 
                             (project.progress.assignedTasks?.length || 0);
  project.progress.percentComplete = Math.round(
    (project.progress.completedTasks.length / pipelineTotalTasks) * 100
  );
  
  // 添加交付成果
  if (update.deliverablePath) {
    project.deliverables.push({
      taskId: update.taskId,
      path: update.deliverablePath,
      submittedAt: update.completedAt,
      submittedBy: update.completedBy
    });
  }
  
  // 更新当前 Agent 状态
  if (project.currentAgent?.task === update.taskId) {
    project.currentAgent = null;
  }
  
  // 更新当前阶段
  if (project.progress.pendingTasks.length === 0 && project.progress.assignedTasks?.length === 0) {
    // 所有任务完成
    project.status = 'completed';
  }
  
  return project;
}

/**
 * 追加历史日志
 */
async function appendHistoryLog(
  projectId: string,
  entry: {
    timestamp: string;
    action: string;
    taskId?: string;
    status?: string;
    completedBy?: string;
  }
): Promise<void> {
  const logPath = `workspace/${projectId}/history.log`;
  const logLine = JSON.stringify(entry) + '\n';
  
  // 追加写入（原子操作）
  const fs = await import('fs/promises');
  await fs.appendFile(logPath, logLine, 'utf-8');
}

/**
 * 更新当前 Agent 信息（派发任务时调用）
 */
export async function updateCurrentAgent(
  projectId: string,
  agentInfo: {
    expertId: string;
    agentId: string;
    sessionKey: string;
    taskId: string;
    assignedAt: string;
  },
  maxRetries = MAX_RETRIES
): Promise<boolean> {
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const projectPath = `workspace/${projectId}/meta.json`;
      const project = await readJson<Project>(projectPath);
      const currentVersion = project.version;
      
      // 更新当前 Agent
      project.currentAgent = {
        expertId: agentInfo.expertId,
        agentId: agentInfo.agentId,
        sessionKey: agentInfo.sessionKey,
        assignedAt: agentInfo.assignedAt,
        task: agentInfo.taskId
      };
      
      // 添加到已分配任务
      if (!project.progress.assignedTasks) {
        project.progress.assignedTasks = [];
      }
      if (!project.progress.assignedTasks.includes(agentInfo.taskId)) {
        project.progress.assignedTasks.push(agentInfo.taskId);
      }
      
      project.version = currentVersion + 1;
      project.updatedAt = new Date().toISOString();
      
      const success = await atomicWriteWithVersionCheck(projectPath, project, currentVersion);
      
      if (success) {
        logger.info(`项目 Agent 更新成功：${projectId} - ${agentInfo.expertId} 分配任务 ${agentInfo.taskId}`);
        return true;
      }
      
      logger.warn(`版本冲突，重试：${projectId}（尝试 ${attempt}/${maxRetries}）`);
      await sleep(100 * attempt);
      
    } catch (error: any) {
      logger.error(`更新 Agent 失败：${projectId}`, error);
      
      if (attempt === maxRetries) {
        return false;
      }
      
      await sleep(100 * attempt);
    }
  }
  
  return false;
}

/**
 * 暂停项目
 */
export async function pauseProject(
  projectId: string,
  reason: string
): Promise<boolean> {
  try {
    const projectPath = `workspace/${projectId}/meta.json`;
    const project = await readJson<Project>(projectPath);
    
    project.status = 'paused';
    project.version++;
    project.updatedAt = new Date().toISOString();
    
    await writeJson(projectPath, project);
    
    await appendHistoryLog(projectId, {
      timestamp: new Date().toISOString(),
      action: 'project_paused',
      status: 'paused'
    });
    
    logger.warn(`项目已暂停：${projectId} - ${reason}`);
    return true;
  } catch (error: any) {
    logger.error(`暂停项目失败：${projectId}`, error);
    return false;
  }
}

/**
 * 辅助函数：sleep
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
