# 调度中心实现指南

## 目录结构

```
proj-system/
├── ARCHITECTURE.md          # 架构设计（本文档的上位设计）
├── README.md                # 使用指南
├── orchestrator/            # 调度中心核心代码
│   ├── index.ts            # 主入口
│   ├── notification.ts     # 通知处理
│   ├── progress.ts         # 进度更新
│   ├── dispatcher.ts       # 任务派发
│   └── session-manager.ts  # Session 管理
├── shared/                  # 共享工具和类型
│   ├── types.ts            # TypeScript 类型定义
│   ├── fs-utils.ts         # 文件系统工具
│   └── logger.ts           # 日志工具
└── agents/                  # Agent 集成
    └── orchestrator/
        └── workspace/       # 调度中心 Agent 工作区
```

## 核心模块实现

### 1. 通知处理器 (notification.ts)

```typescript
import { readJson, writeJson } from '../shared/fs-utils';
import { logger } from '../shared/logger';
import { Notification, Project } from '../shared/types';

/**
 * 处理 Agent 完成通知
 */
export async function handleNotification(notification: Notification): Promise<void> {
  const { projectId, taskId, agentId, deliverablePath, status } = notification;
  
  logger.info(`收到完成通知：${projectId}/${taskId} by ${agentId}`);
  
  // 1. 验证通知格式
  if (!validateNotification(notification)) {
    throw new Error(`无效的通知格式：${JSON.stringify(notification)}`);
  }
  
  // 2. 更新项目进度
  await updateProjectProgress(projectId, {
    taskId,
    status,
    deliverablePath,
    completedAt: new Date().toISOString(),
    completedBy: agentId
  });
  
  // 3. 查找下一个任务
  const nextTask = await findNextTask(projectId, taskId);
  
  if (nextTask) {
    // 4. 派发下一个任务
    await dispatchNextTask(projectId, nextTask);
  } else {
    // 5. 项目完成
    await handleProjectCompletion(projectId);
  }
  
  logger.info(`通知处理完成：${projectId}/${taskId}`);
}

function validateNotification(notification: Notification): boolean {
  return !!(
    notification.projectId &&
    notification.taskId &&
    notification.agentId &&
    notification.status
  );
}
```

### 2. 进度更新器 (progress.ts)

```typescript
import { readJson, writeJson, withFileLock } from '../shared/fs-utils';
import { Project, TaskProgress } from '../shared/types';

/**
 * 更新项目进度（线程安全）
 */
export async function updateProjectProgress(
  projectId: string,
  taskProgress: TaskProgress
): Promise<void> {
  const projectPath = `workspace/${projectId}/project.json`;
  
  await withFileLock(`${projectPath}.lock`, async () => {
    const project = await readJson<Project>(projectPath);
    
    // 更新已完成任务列表
    if (!project.progress.completedTasks.includes(taskProgress.taskId)) {
      project.progress.completedTasks.push(taskProgress.taskId);
    }
    
    // 从未完成任务中移除
    project.progress.pendingTasks = project.progress.pendingTasks.filter(
      id => id !== taskProgress.taskId
    );
    
    // 更新进度百分比
    const totalTasks = project.pipeline.totalTasks;
    const completedCount = project.progress.completedTasks.length;
    project.progress.percentComplete = Math.round((completedCount / totalTasks) * 100);
    
    // 记录交付成果
    if (taskProgress.deliverablePath) {
      project.deliverables.push({
        taskId: taskProgress.taskId,
        path: taskProgress.deliverablePath,
        submittedAt: taskProgress.completedAt,
        submittedBy: taskProgress.completedBy
      });
    }
    
    // 更新当前 Agent 状态
    project.currentAgent = null; // 清空，等待下一个任务分配
    
    // 更新时间戳
    project.updatedAt = new Date().toISOString();
    
    // 原子写入
    await writeJson(projectPath, project);
  });
  
  logger.info(`项目进度已更新：${projectId} - ${project.progress.percentComplete}%`);
}
```

### 3. 任务派发器 (dispatcher.ts)

```typescript
import { readJson } from '../shared/fs-utils';
import { sessions_send } from '@openclaw/sessions';
import { Pipeline, Task, Project } from '../shared/types';

/**
 * 查找下一个可执行的任务
 */
export async function findNextTask(
  projectId: string,
  completedTaskId: string
): Promise<Task | null> {
  const pipeline = await readJson<Pipeline>(`workspace/${projectId}/pipeline.json`);
  const project = await readJson<Project>(`workspace/${projectId}/project.json`);
  
  // 找到所有依赖当前任务的任务
  const allTasks = pipeline.phases.flatMap(phase => phase.tasks);
  const dependentTasks = allTasks.filter(task =>
    task.dependencies?.includes(completedTaskId)
  );
  
  // 检查依赖是否全部满足
  for (const task of dependentTasks) {
    if (project.progress.pendingTasks.includes(task.id)) {
      const allDepsCompleted = task.dependencies?.every(depId =>
        project.progress.completedTasks.includes(depId)
      );
      
      if (allDepsCompleted) {
        return task;
      }
    }
  }
  
  return null;
}

/**
 * 派发任务到 Agent Session
 */
export async function dispatchNextTask(
  projectId: string,
  task: Task
): Promise<void> {
  const project = await readJson<Project>(`workspace/${projectId}/project.json`);
  const pipeline = await readJson<Pipeline>(`workspace/${projectId}/pipeline.json`);
  
  // 获取专家 Agent 的 session
  const sessionInfo = await getSessionForExpert(task.expertId);
  
  if (!sessionInfo) {
    // 如果没有现成 session，spawn 一个新的
    const newSession = await spawnAgentSession(task.expertId);
    await dispatchTaskToSession(newSession, projectId, task, pipeline);
  } else {
    await dispatchTaskToSession(sessionInfo, projectId, task, pipeline);
  }
  
  logger.info(`任务已派发：${task.id} -> ${task.expertId}`);
}

async function dispatchTaskToSession(
  session: { sessionKey: string; agentId: string },
  projectId: string,
  task: Task,
  pipeline: Pipeline
): Promise<void> {
  // 收集上游成果
  const upstreamDeliverables = await collectUpstreamDeliverables(projectId, task);
  
  // 构造派单消息
  const message = buildDispatchMessage(projectId, task, upstreamDeliverables);
  
  // 发送到 Agent session
  await sessions_send({
    sessionKey: session.sessionKey,
    message: message
  });
  
  // 更新项目状态
  await updateCurrentAgent(projectId, {
    expertId: task.expertId,
    agentId: session.agentId,
    sessionKey: session.sessionKey,
    taskId: task.id,
    assignedAt: new Date().toISOString()
  });
}

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
${upstreamDeliverables.map((path, i) => `- ${path}`).join('\n')}

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
```

### 4. Session 管理器 (session-manager.ts)

```typescript
import { readJson, writeJson } from '../shared/fs-utils';
import { sessions_spawn } from '@openclaw/sessions';

interface SessionRegistry {
  [expertId: string]: {
    agentId: string;
    sessionKey: string;
    createdAt: string;
    lastUsedAt: string;
  };
}

const REGISTRY_PATH = 'proj-system/.sessions.json';

/**
 * 获取专家的 Session（复用优先）
 */
export async function getSessionForExpert(expertId: string): Promise<{
  sessionKey: string;
  agentId: string;
} | null> {
  const registry = await readJson<SessionRegistry>(REGISTRY_PATH, {});
  
  if (registry[expertId]) {
    const session = registry[expertId];
    // 更新最后使用时间
    session.lastUsedAt = new Date().toISOString();
    await writeJson(REGISTRY_PATH, registry);
    
    return {
      sessionKey: session.sessionKey,
      agentId: session.agentId
    };
  }
  
  return null;
}

/**
 * Spawn 新的 Agent Session
 */
export async function spawnAgentSession(expertId: string): Promise<{
  sessionKey: string;
  agentId: string;
}> {
  const result = await sessions_spawn({
    task: `你是一个通过专家文件初始化的专业 subagent。

## 阶段 A：初始化专家身份

依次读取以下三个文件，加载你的专家身份：

1. ${process.cwd()}/skills/find-expert-skills/experts/${expertId}/IDENTITY.md
2. ${process.cwd()}/skills/find-expert-skills/experts/${expertId}/SOUL.md
3. ${process.cwd()}/skills/find-expert-skills/experts/${expertId}/AGENTS.md

读取完成后，你就是这位专家。后续所有行为符合这三个文件定义的身份、规则和风格。

## 阶段 B：等待任务

等待调度中心派发任务。收到任务后，以专家身份执行，遵循 SOUL.md 沟通风格，按 AGENTS.md 工作流程推进。

**重要：** 任务完成后，必须执行以下 3 个步骤：
1. 将成果保存到指定目录
2. 更新项目的 project.json 进度
3. 发送【任务完成通知】到调度中心`,
    label: `expert-${expertId}`,
    runtime: 'subagent',
    mode: 'session',
    cleanup: 'keep'
  });
  
  // 注册 session
  const registry = await readJson<SessionRegistry>(REGISTRY_PATH, {});
  registry[expertId] = {
    agentId: result.agentId,
    sessionKey: result.sessionKey,
    createdAt: new Date().toISOString(),
    lastUsedAt: new Date().toISOString()
  };
  await writeJson(REGISTRY_PATH, registry);
  
  return {
    sessionKey: result.sessionKey,
    agentId: result.agentId
  };
}
```

## Agent 集成指南

### Expert Agent 完成工作后的标准流程

每个专家 Agent 在完成任务后，必须执行以下代码：

```typescript
// 在 Agent 代码中
async function completeTask(taskId: string, deliverablePath: string) {
  // 1. 保存成果
  await saveDeliverable(deliverablePath, output);
  
  // 2. 更新项目进度
  await updateProjectProgress(projectId, {
    taskId,
    status: 'completed',
    deliverablePath,
    completedAt: new Date().toISOString()
  });
  
  // 3. 发送通知到调度中心
  await sendNotification({
    projectId,
    taskId,
    agentId: myAgentId,
    expertId: myExpertId,
    deliverablePath,
    status: 'completed',
    message: `任务 ${taskId} 已完成，成果在 ${deliverablePath}`
  });
  
  console.log('✅ 任务完成，已通知调度中心');
}
```

### 通知发送函数

```typescript
import { sessions_send } from '@openclaw/sessions';

const ORCHESTRATOR_SESSION = 'orchestrator-main'; // 调度中心的 session

async function sendNotification(notification: {
  projectId: string;
  taskId: string;
  agentId: string;
  expertId: string;
  deliverablePath: string;
  status: 'completed' | 'failed';
  message?: string;
}): Promise<void> {
  const message = `【任务完成通知】

项目编号：${notification.projectId}
任务 ID：${notification.taskId}
任务名称：[从 pipeline.json 读取]
执行 Agent：${notification.expertId}

完成情况：
- 状态：${notification.status === 'completed' ? '✅ 已完成' : '❌ 失败'}
- 成果路径：${notification.deliverablePath}
- 耗时：[计算耗时]
- 备注：${notification.message || '无'}

请调度中心安排下一步工作。`;

  await sessions_send({
    sessionKey: ORCHESTRATOR_SESSION,
    message
  });
}
```

## 测试清单

- [ ] 通知格式验证
- [ ] 进度更新原子性
- [ ] 任务依赖检查
- [ ] Session 复用逻辑
- [ ] 并发写入保护
- [ ] 异常回滚机制
- [ ] 日志记录完整性

---

**版本：** v1.0  
**更新日期：** 2026-03-19
