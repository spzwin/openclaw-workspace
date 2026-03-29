# 核心机制实现指南

> 📅 **更新日期：** 2026-03-19  
> 🎯 **目标：** 落地通知队列 + Session 健康检查 + 乐观锁

---

## ✅ 已完成的核心机制

### 1. 通知队列（持久化）

**文件：** `orchestrator/notification-queue.ts`

**功能：**
- ✅ 入队通知（原子写入）
- ✅ 出队处理（FIFO）
- ✅ 重试机制（最多 3 次）
- ✅ 状态跟踪（pending/processing/completed/failed）
- ✅ 定期清理（24 小时）

**目录结构：**
```
proj-system/.queue/
├── pending/      # 待处理通知
├── processing/   # 处理中通知
├── completed/    # 已完成通知
├── failed/       # 失败通知
└── queue-state.json
```

**使用示例：**
```typescript
import { enqueueNotification } from './orchestrator/notification-queue';

// Agent 提交通知
await enqueueNotification({
  id: 'notif-xxx',
  projectId: 'PROJ-20260319-001',
  taskId: 'RT01',
  agentId: 'agent-xxx',
  expertId: 'expert-bd',
  deliverablePath: 'workspace/PROJ-20260319-001/RT01_BD_Analysis/deliverables/bd_report.md',
  status: 'completed',
  timestamp: new Date().toISOString()
});
```

---

### 2. Session 健康检查

**文件：** `orchestrator/session-manager.ts`

**功能：**
- ✅ 定期健康检查（60 秒）
- ✅ Session 状态跟踪（active/idle/error/offline）
- ✅ 自动恢复（异常 Session 重新创建）
- ✅ 空闲清理（24 小时未使用）

**注册表：** `proj-system/.sessions.json`

**状态流转：**
```
创建 → active → idle → (健康检查) → active/error
                          ↓
                    error → 重新创建 → active
```

---

### 3. 乐观锁更新

**文件：** `orchestrator/project-manager.ts`

**功能：**
- ✅ 版本号管理（version 字段）
- ✅ 原子写入（临时文件 + 重命名）
- ✅ 版本检查（冲突时重试）
- ✅ 最多重试 3 次

**Project 结构更新：**
```json
{
  "id": "PROJ-20260319-001",
  "version": 1,  // ← 新增
  "status": "in_progress",
  ...
}
```

**使用示例：**
```typescript
import { updateProjectProgress } from './orchestrator/project-manager';

const success = await updateProjectProgress('PROJ-20260319-001', {
  taskId: 'RT01',
  status: 'completed',
  deliverablePath: 'workspace/.../bd_report.md',
  completedAt: new Date().toISOString(),
  completedBy: 'expert-bd'
});

if (!success) {
  // 处理失败（版本冲突或写入错误）
}
```

---

### 4. Agent 状态管理

**文件：** `orchestrator/agent-status-manager.ts`

**功能：**
- ✅ 个人状态文件（`proj-system/agents/{expertId}/status.json`）
- ✅ 工作区状态文件（`workspace/{projectId}/{expertId}-status.json`）
- ✅ 任务进度跟踪
- ✅ 历史记录
- ✅ 心跳机制

**个人状态文件结构：**
```json
{
  "expertId": "expert-bd",
  "agentId": "agent-xxx",
  "sessionKey": "session-xxx",
  "currentTask": {
    "projectId": "PROJ-20260319-001",
    "taskId": "RT01",
    "taskName": "BD 初审",
    "assignedAt": "2026-03-19T08:00:00Z",
    "status": "working",
    "progress": 50,
    "lastUpdate": "2026-03-19T09:00:00Z"
  },
  "taskHistory": [...],
  "capabilities": ["需求分析", "客户沟通"],
  "status": "busy",
  "updatedAt": "2026-03-19T09:00:00Z"
}
```

**Agent 工作流程：**
```
1. 接收任务 → agentStartTask()
2. 更新进度 → agentUpdateProgress(50)
3. 切换阶段 → updateAgentWorkspaceStatus({ phase: 'drafting' })
4. 完成任务 → agentCompleteTask(deliverablePath, 'completed')
5. 提交通知 → enqueueNotification(...)
```

---

## 📁 示例项目结构

**模板路径：** `proj-system/templates/sample-project/`

**目录结构：**
```
workspace/PROJ-20260319-001/
├── meta.json              # 项目元数据（含 version）
├── pipeline.json          # 任务编排流程
├── history.log            # 状态日志（追加）
├── RT01_BD_Analysis/
│   ├── readme.md
│   ├── agent-status.json  # Agent 工作区状态
│   ├── drafts/
│   ├── research/
│   └── deliverables/
│       └── bd_report.md   # 完成后生成
├── RT02_Research_Analysis/
│   └── ...
├── RT03_Mid_Review/
│   └── ...
└── RT04_Final_Review/
    └── ...
```

---

## 🔄 完整流程示例（RT01→RT04）

### 阶段 1: 项目初始化

```typescript
// 1. 复制模板
cp -r proj-system/templates/sample-project workspace/PROJ-20260319-001

// 2. 初始化 Agent 状态
await createAgentStatus('expert-bd', 'agent-001', 'session-001');
await createAgentStatus('expert-research', 'agent-002', 'session-002');
await createAgentStatus('expert-mid-review', 'agent-003', 'session-003');
await createAgentStatus('expert-final-review', 'agent-004', 'session-004');

// 3. 启动调度中心
await startOrchestrator();
```

### 阶段 2: 派发 RT01 和 RT02（并行）

```typescript
// 调度中心自动查找可执行任务
const nextTasks = await findNextTasks('PROJ-20260319-001');
// 返回：[RT01, RT02]（无依赖）

// 派发 RT01
await dispatchTaskWithRetry('PROJ-20260319-001', {
  id: 'RT01',
  expertId: 'expert-bd',
  name: 'BD 初审',
  ...
});

// 派发 RT02
await dispatchTaskWithRetry('PROJ-20260319-001', {
  id: 'RT02',
  expertId: 'expert-research',
  name: '创研初审',
  ...
});
```

### 阶段 3: Agent 执行任务

```typescript
// expert-bd 接收任务
await agentStartTask('expert-bd', 'PROJ-20260319-001', 'RT01', 'BD 初审');

// 更新工作区状态
await updateAgentWorkspaceStatus('PROJ-20260319-001', 'expert-bd', {
  phase: 'research',
  log: [{ timestamp: now, action: 'started_research' }]
});

// 执行工作...
// 创建草稿：RT01_BD_Analysis/drafts/v1.md
// 调研资料：RT01_BD_Analysis/research/...

// 更新进度
await agentUpdateProgress('expert-bd', 50);
await updateAgentWorkspaceStatus('PROJ-20260319-001', 'expert-bd', {
  phase: 'drafting'
});

// 完成工作
await agentUpdateProgress('expert-bd', 100);
await updateAgentWorkspaceStatus('PROJ-20260319-001', 'expert-bd', {
  phase: 'submitting',
  deliverables: ['RT01_BD_Analysis/deliverables/bd_report.md']
});

// 提交成果
await agentCompleteTask('expert-bd', 'workspace/PROJ-20260319-001/RT01_BD_Analysis/deliverables/bd_report.md');

// 提交通知到调度中心
await enqueueNotification({
  projectId: 'PROJ-20260319-001',
  taskId: 'RT01',
  expertId: 'expert-bd',
  deliverablePath: 'workspace/PROJ-20260319-001/RT01_BD_Analysis/deliverables/bd_report.md',
  status: 'completed',
  timestamp: new Date().toISOString()
});
```

### 阶段 4: 调度中心处理通知

```typescript
// 调度中心接收通知
await handleNotification(notification);

// 1. 验证通知格式 ✓
// 2. 更新项目进度（乐观锁）
await updateProjectProgress('PROJ-20260319-001', {...});
// meta.json version: 1 → 2

// 3. 查找下一个任务
const nextTasks = await findNextTasks('PROJ-20260319-001');
// RT01 完成，但 RT02 还在进行中 → 无新任务

// 等待 RT02 完成...
```

### 阶段 5: RT02 完成，触发 RT03

```typescript
// RT02 提交通知
await enqueueNotification({...});

// 调度中心处理
await handleNotification(notification);

// 更新项目进度
// meta.json version: 2 → 3

// 查找下一个任务
const nextTasks = await findNextTasks('PROJ-20260319-001');
// RT01 ✅, RT02 ✅ → RT03 可执行！
// 返回：[RT03]

// 派发 RT03
await dispatchTaskWithRetry('PROJ-20260319-001', RT03_task);
```

### 阶段 6: RT03 → RT04 → 项目完成

```typescript
// 重复上述流程...
// RT03 完成 → 触发 RT04
// RT04 完成 → 项目状态变为 completed
```

---

## 🔧 集成到 OpenClaw

### 需要实现的 OpenClaw 调用

**1. Session 创建（session-manager.ts）**
```typescript
// 替换伪代码
const session = await sessions_spawn({
  task: `你是 ${expertId}，负责...`,
  label: `expert-${expertId}`,
  runtime: 'subagent',
  mode: 'session',
  thread: true
});

sessionInfo.sessionKey = session.sessionKey;
sessionInfo.agentId = session.agentId;
```

**2. 消息发送（session-manager.ts）**
```typescript
// 替换伪代码
await sessions_send({
  sessionKey: session.sessionKey,
  message: buildDispatchMessage(...)
});
```

**3. 通知监听（index.ts）**
```typescript
// 需要监听 sessions 消息
// 当收到通知格式的消息时，调用 handleIncomingNotification
```

---

## 📋 检查清单

### 核心机制
- [x] 通知队列持久化
- [x] 通知重试机制
- [x] Session 健康检查
- [x] Session 自动恢复
- [x] 乐观锁更新
- [x] Agent 状态管理
- [x] Agent 工作区状态

### 示例项目
- [x] meta.json（含 version）
- [x] pipeline.json（RT01→RT04）
- [x] RT 目录结构
- [x] Agent 状态文件模板

### 待实现
- [ ] OpenClaw sessions_spawn 集成
- [ ] OpenClaw sessions_send 集成
- [ ] 通知监听器（消息回调）
- [ ] 实际运行测试

---

## 🚀 下一步

1. **集成 OpenClaw API** - 替换 session-manager.ts 中的伪代码
2. **创建真实 Agent** - 为 4 个专家创建实际的 SOUL.md 等配置文件
3. **运行测试** - 手动触发 RT01，验证完整流程
4. **监控调优** - 根据实际运行情况调整参数（健康检查间隔、重试次数等）
