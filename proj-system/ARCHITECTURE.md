# 事件驱动调度中心 v2

## 核心架构

### 从轮询到事件驱动

**旧模式（定时器轮询）：**
```
定时器 → 检查所有项目进度 → 发现有完成的 → 派发下一步
问题：浪费资源、延迟高、实现复杂
```

**新模式（事件驱动）：**
```
Agent 完成 → 提交通知 → 调度中心立即处理 → 派发下一步
优势：实时、高效、简单可靠
```

## 工作流程

### Agent 完成工作后的标准流程

```
┌──────────────────────────────────────────────────────────────┐
│  Expert Agent 完成工作后，必须执行以下 3 个步骤：              │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Step 1  │        │ Step 2  │        │ Step 3  │
   │ 提交成果 │        │ 更新进度 │        │ 发送通知 │
   └─────────┘        └─────────┘        └─────────┘
        │                   │                   │
        ▼                   ▼                   ▼
  保存到项目目录        更新 project.json   发送 session 消息
  (workspace/{project}/  (status, progress,  到调度中心
   deliverables/)        completed_tasks)
```

### 调度中心处理流程

```
┌──────────────────────────────────────────────────────────────┐
│  调度中心收到通知后：                                          │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ 1. 读取  │        │ 2. 查找  │        │ 3. 派发  │
   │ project  │        │ 下一步   │        │ 给下一个 │
   │ .json    │        │ 任务配置 │        │ Agent   │
   └─────────┘        └─────────┘        └─────────┘
        │                   │                   │
        ▼                   ▼                   ▼
   当前项目状态         根据 pipeline        sessions_send
   和已完成任务         找到下一个执行者      (task, context)
```

## 项目数据结构

### 项目目录结构

```
workspace/
└── {project-id}/
    ├── project.json          # 项目元数据和进度
    ├── pipeline.json         # 任务编排流程
    ├── deliverables/         # 交付成果
    │   ├── phase-1/
    │   └── phase-2/
    └── context/              # 共享上下文
        └── ...
```

### project.json 格式

```json
{
  "id": "proj-001",
  "name": "项目名称",
  "status": "in_progress",  // pending | in_progress | completed | paused
  "createdAt": "2026-03-19T00:00:00Z",
  "updatedAt": "2026-03-19T08:00:00Z",
  
  "progress": {
    "currentPhase": "phase-2",
    "completedTasks": ["task-001", "task-002"],
    "pendingTasks": ["task-003", "task-004"],
    "percentComplete": 50
  },
  
  "currentAgent": {
    "expertId": "engineering-frontend-developer",
    "agentId": "agent-xxx-xxx",
    "sessionKey": "session-yyy-yyy",
    "assignedAt": "2026-03-19T06:00:00Z",
    "task": "task-002"
  },
  
  "deliverables": [
    {
      "taskId": "task-001",
      "path": "workspace/proj-001/deliverables/phase-1/output.md",
      "submittedAt": "2026-03-19T04:00:00Z",
      "submittedBy": "engineering-backend-architect"
    }
  ]
}
```

### pipeline.json 格式

```json
{
  "projectId": "proj-001",
  "phases": [
    {
      "id": "phase-1",
      "name": "需求分析与设计",
      "tasks": [
        {
          "id": "task-001",
          "name": "需求分析",
          "expertId": "product-manager",
          "description": "分析用户需求，输出 PRD",
          "dependencies": [],
          "outputPath": "deliverables/phase-1/prd.md"
        },
        {
          "id": "task-002",
          "name": "技术方案设计",
          "expertId": "engineering-software-architect",
          "description": "基于 PRD 设计技术架构",
          "dependencies": ["task-001"],
          "outputPath": "deliverables/phase-1/architecture.md"
        }
      ]
    },
    {
      "id": "phase-2",
      "name": "开发实现",
      "tasks": [
        {
          "id": "task-003",
          "name": "前端开发",
          "expertId": "engineering-frontend-developer",
          "description": "实现前端界面",
          "dependencies": ["task-002"],
          "outputPath": "deliverables/phase-2/frontend/"
        },
        {
          "id": "task-004",
          "name": "后端开发",
          "expertId": "engineering-backend-architect",
          "description": "实现后端 API",
          "dependencies": ["task-002"],
          "dependencies": ["task-002"],
          "outputPath": "deliverables/phase-2/backend/"
        }
      ]
    }
  ]
}
```

## 通知协议

### Agent → 调度中心（通知消息格式）

```markdown
【任务完成通知】

项目编号：proj-001
任务 ID：task-002
任务名称：技术方案设计
执行 Agent：engineering-software-architect

完成情况：
- 状态：✅ 已完成
- 成果路径：workspace/proj-001/deliverables/phase-1/architecture.md
- 耗时：2 小时
- 备注：架构设计已完成，包含 3 个核心模块

请调度中心安排下一步工作。
```

### 调度中心 → Next Agent（派单消息格式）

```markdown
【新任务派发】

项目编号：proj-001
任务 ID：task-003
任务名称：前端开发

上游依赖：
- task-002（技术方案设计）✅ 已完成
  成果：workspace/proj-001/deliverables/phase-1/architecture.md

任务描述：
基于架构设计文档，实现前端界面

输出要求：
- 路径：workspace/proj-001/deliverables/phase-2/frontend/
- 格式：可运行的代码 + README

上下文：
- 项目文档：workspace/proj-001/context/
- 前置成果：workspace/proj-001/deliverables/phase-1/

请开始执行，完成后提交通知。
```

## 调度中心职责

### 核心函数

1. **receiveNotification(notification)**
   - 接收 Agent 完成通知
   - 解析项目编号、任务 ID、成果路径

2. **updateProjectProgress(projectId, taskData)**
   - 更新 project.json
   - 标记任务完成
   - 记录交付成果

3. **findNextTask(projectId, completedTaskId)**
   - 读取 pipeline.json
   - 找到依赖当前任务的下一个任务
   - 检查依赖是否全部满足

4. **dispatchTask(nextTask, agentSession)**
   - 构造派单消息
   - 发送到对应 Agent 的 session
   - 更新 currentAgent 字段

5. **handleCompletion(projectId)**
   - 所有任务完成
   - 更新项目状态为 completed
   - 发送项目完成通知

## 异常处理

### Agent 执行失败

```
Agent 报告失败 → 调度中心记录失败原因 → 通知人工介入
或 → 自动重试（最多 2 次）
或 → 重新分配给其他 Agent
```

### 依赖任务阻塞

```
任务 A 依赖任务 B → 任务 B 延期 → 调度中心检测超时
→ 通知项目 Owner → 调整优先级或资源
```

### 通知丢失

```
Agent 发送通知后未收到确认 → 超时重试（30 秒后）
→ 仍无响应 → 降级：直接更新 project.json 并继续
```

## 实现要点

### Session 管理

- 每个专家 Agent 使用持久化 session（`mode: "session"`）
- 调度中心维护 session 注册表（`.sessions.json`）
- 优先复用已有 session，避免重复 spawn

### 文件锁

- 更新 project.json 时使用文件锁
- 避免并发写入冲突
- 使用原子操作（写入临时文件 → 重命名）

### 日志

- 所有通知和派单记录到 `logs/orchestrator.log`
- 包含时间戳、项目编号、任务 ID、操作类型
- 便于审计和问题排查

## 迁移指南

### 从定时器轮询迁移到事件驱动

1. 保留现有 pipeline.json 格式
2. 为每个 Agent 添加提交通知的逻辑
3. 部署调度中心监听器
4. 关闭定时器任务
5. 验证事件流正常工作

---

**版本：** v2.0  
**更新日期：** 2026-03-19  
**设计原则：** 事件驱动、实时响应、简单可靠
