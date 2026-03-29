// 健康监控 - 检查卡住的项目和异常状态

import { readJson, writeJson } from '../shared/fs-utils';
import { logger } from '../shared/logger';
import { Project } from '../shared/types';

const STUCK_THRESHOLD_MS = 24 * 60 * 60 * 1000; // 24 小时

/**
 * 检查所有卡住的项目
 */
export async function checkStuckProjects(): Promise<void> {
  logger.info('检查卡住的项目...');
  
  // 获取所有项目目录
  const projects = await getAllProjects();
  
  let stuckCount = 0;
  
  for (const project of projects) {
    const isStuck = await checkProjectHealth(project.id);
    if (isStuck) {
      stuckCount++;
    }
  }
  
  if (stuckCount > 0) {
    logger.warn(`发现 ${stuckCount} 个卡住的项目`);
  } else {
    logger.info('所有项目状态正常');
  }
}

/**
 * 检查单个项目健康状态
 */
export async function checkProjectHealth(projectId: string): Promise<boolean> {
  try {
    const projectPath = `workspace/${projectId}/project.json`;
    const project = await readJson<Project>(projectPath);
    
    // 只检查进行中的项目
    if (project.status !== 'in_progress') {
      return false;
    }
    
    const lastUpdate = new Date(project.updatedAt).getTime();
    const timeSinceLastUpdate = Date.now() - lastUpdate;
    
    if (timeSinceLastUpdate > STUCK_THRESHOLD_MS) {
      logger.warn(
        `项目可能卡住：${projectId}（${Math.round(timeSinceLastUpdate / 1000 / 3600)} 小时未更新）`
      );
      
      // 分析卡住原因
      await analyzeStuckReason(project);
      
      return true;
    }
    
    return false;
    
  } catch (error: any) {
    logger.error(`检查项目健康失败：${projectId}`, error);
    return false;
  }
}

/**
 * 分析卡住原因
 */
async function analyzeStuckReason(project: Project): Promise<void> {
  const hasPendingTasks = project.progress.pendingTasks.length > 0;
  const hasAssignedTasks = project.progress.assignedTasks?.length > 0;
  
  if (hasPendingTasks && !hasAssignedTasks) {
    // 有待处理任务，但没有分配中的任务 → 可能漏了派发
    logger.warn(`项目有待处理任务但未分配：${project.id}`);
    logger.warn(`待处理任务：${project.progress.pendingTasks.join(', ')}`);
    
    // 尝试重新派发
    // await triggerDispatch(project.id);
  }
  
  if (hasAssignedTasks) {
    // 有分配中的任务，但长时间未完成 → Agent 可能卡住
    logger.warn(`项目有任务长时间未完成情况：${project.id}`);
    logger.warn(`分配中的任务：${project.progress.assignedTasks?.join(', ')}`);
    
    if (project.currentAgent) {
      logger.warn(`当前 Agent：${project.currentAgent.expertId}`);
      // 检查 Agent session 状态
      // await checkAgentSession(project.currentAgent.sessionKey);
    }
  }
}

/**
 * 获取所有项目
 */
async function getAllProjects(): Promise<{ id: string }[]> {
  // 伪代码：读取 workspace 目录下所有包含 project.json 的目录
  // const dirs = await fs.readdir('workspace');
  // const projects = [];
  // for (const dir of dirs) {
  //   if (await fs.exists(`workspace/${dir}/project.json`)) {
  //     projects.push({ id: dir });
  //   }
  // }
  // return projects;
  
  return [{ id: 'demo-001' }]; // 临时返回
}
