# 事件驱动调度中心 - 使用指南

## 快速开始

### 1. 创建新项目

```bash
mkdir -p workspace/proj-001/{deliverables,context}
```

创建 `project.json`:
```json
{
  "id": "proj-001",
  "name": "我的项目",
  "status": "pending",
  "createdAt": "2026-03-19T00:00:00Z",
  "updatedAt": "2026-03-19T00:00:00Z",
  "progress": {
    "currentPhase": "phase-1",
    "completedTasks": [],
    "pendingTasks": ["task-001", "task-002"],
    "percentComplete": 0
  },
  "currentAgent": null,
  "deliverables": []
}
```

创建 `pipeline.json`:
```json
{
  "projectId": "proj-001",
  "phases": [
    {
      "id": "phase-1",
      "name": "需求与设计",
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
          "name": "技术方案",
          "expertId": "engineering-software-architect",
          "description": "基于 PRD 设计技术架构",
          "dependencies": ["task-001"],
          "outputPath": "deliverables/phase-1/architecture.md"
        }
      ]
    }
  ]
}
```

### 2. 启动调度中心

调度中心是一个常驻的 Agent Session，监听任务完成通知。

**启动命令：**
```
/spawn 调度中心
```

或使用 OpenClaw API:
```typescript
await sessions_spawn({
  task: '你是调度中心，负责监听任务完成通知并编排下一步工作',
  label: 'orchestrator',
  runtime: 'subagent',
  mode: 'session',
  cleanup: 'keep'
});
```

### 3. 派发第一个任务

手动或通过 API 发送第一个任务到对应专家的 session:

```markdown
【新任务派发】

项目编号：proj-001
任务 ID：task-001
任务名称：需求分析

任务描述：
分析用户需求，输出 PRD 文档

输出要求：
- 路径：workspace/proj-001/deliverables/phase-1/prd.md
- 格式：Markdown 文档

请开始执行，完成后提交通知。
```

### 4. Agent 执行并提交通知

专家 Agent 完成任务后，发送通知：

```markdown
【任务完成通知】

项目编号：proj-001
任务 ID：task-001
任务名称：需求分析
执行 Agent：product-manager

完成情况：
- 状态：✅ 已完成
- 成果路径：workspace/proj-001/deliverables/phase-1/prd.md
- 耗时：1.5 小时
- 备注：PRD 已包含用户故事、功能列表和验收标准

请调度中心安排下一步工作。
```

### 5. 调度中心自动派发下一步

调度中心收到通知后：
1. 更新 `project.json` 进度
2. 查找下一个任务（task-002）
3. 派发给 `engineering-software-architect`

循环继续，直到所有任务完成。

## 通知模板

### Agent → 调度中心（完成通知）

```markdown
【任务完成通知】

项目编号：{project-id}
任务 ID：{task-id}
任务名称：{task-name}
执行 Agent：{expert-id}

完成情况：
- 状态：✅ 已完成 / ❌ 失败
- 成果路径：{deliverable-path}
- 耗时：{duration}
- 备注：{notes}

请调度中心安排下一步工作。
```

### 调度中心 → Agent（派单通知）

```markdown
【新任务派发】

项目编号：{project-id}
任务 ID：{task-id}
任务名称：{task-name}

上游依赖：
- {completed-task-id}（{task-name}）✅ 已完成
  成果：{deliverable-path}

任务描述：
{task-description}

输出要求：
- 路径：{output-path}
- 格式：{format-requirements}

上下文：
- 项目文档：workspace/{project-id}/context/
- 前置成果：workspace/{project-id}/deliverables/

请开始执行，完成后提交通知。
```

## 项目管理

### 查看项目进度

```bash
cat workspace/proj-001/project.json
```

### 查看任务编排

```bash
cat workspace/proj-001/pipeline.json
```

### 查看所有交付成果

```bash
ls -R workspace/proj-001/deliverables/
```

## 常见问题

### Q: Agent 没有提交通知怎么办？

**A:** 检查 Agent 是否正确集成了提交流程。参考 `IMPLEMENTATION.md` 的"Agent 集成指南"部分。

临时方案：手动更新 `project.json` 并触发调度中心：

```markdown
【手动进度更新】

项目编号：proj-001
任务 ID：task-001
状态：已完成
成果路径：workspace/proj-001/deliverables/phase-1/prd.md

请调度中心继续编排。
```

### Q: 如何暂停项目？

**A:** 修改 `project.json`:

```json
{
  "status": "paused",
  "pausedAt": "2026-03-19T10:00:00Z",
  "pausedReason": "等待客户确认需求"
}
```

调度中心检测到 `status: "paused"` 时会暂停编排。

### Q: 如何添加紧急任务？

**A:** 更新 `pipeline.json`，在对应 phase 添加任务：

```json
{
  "phases": [
    {
      "id": "phase-1",
      "tasks": [
        {
          "id": "task-001",
          ...
        },
        {
          "id": "task-001-urgent",
          "name": "紧急修复",
          "expertId": "engineering-senior-developer",
          "description": "...",
          "dependencies": [],
          "outputPath": "deliverables/phase-1/hotfix.md",
          "priority": "urgent"
        }
      ]
    }
  ]
}
```

然后手动派发给对应 Agent。

### Q: 多个任务可以并行吗？

**A:** 可以！在 `pipeline.json` 中设置相同的依赖：

```json
{
  "tasks": [
    {
      "id": "task-003",
      "name": "前端开发",
      "dependencies": ["task-002"]
    },
    {
      "id": "task-004",
      "name": "后端开发",
      "dependencies": ["task-002"]
    }
  ]
}
```

当 task-002 完成后，调度中心会同时派发 task-003 和 task-004。

## 最佳实践

### 1. 任务拆分原则

- 每个任务应该是**可独立交付**的
- 任务之间依赖关系要**清晰明确**
- 单个任务执行时间建议在 **2-8 小时**
- 避免过细的拆分（增加协调成本）

### 2. 成果保存规范

```
workspace/{project-id}/
├── deliverables/
│   ├── phase-1/
│   │   ├── prd.md              # 需求文档
│   │   └── architecture.md     # 架构设计
│   └── phase-2/
│       ├── frontend/           # 前端代码
│       └── backend/            # 后端代码
└── context/
    └── meeting-notes.md        # 会议记录
```

### 3. 通知及时性

- Agent 完成任务后**立即**提交通知
- 不要累积多个任务一起提交
- 失败也要提交通知（便于及时处理）

### 4. Session 复用

- 同一专家在同一项目中**复用 session**
- 避免频繁 spawn 新 session（节省资源）
- 定期清理长期未使用的 session

## 监控与日志

### 调度中心日志

```bash
tail -f proj-system/logs/orchestrator.log
```

日志格式：
```
[2026-03-19 08:00:00] INFO 收到完成通知：proj-001/task-001 by product-manager
[2026-03-19 08:00:01] INFO 项目进度已更新：proj-001 - 50%
[2026-03-19 08:00:02] INFO 找到下一个任务：task-002
[2026-03-19 08:00:03] INFO 任务已派发：task-002 -> engineering-software-architect
```

### 项目状态查询

```bash
# 查看正在进行的项目
find workspace -name "project.json" | xargs grep -l '"status": "in_progress"'

# 查看已完成的项目
find workspace -name "project.json" | xargs grep -l '"status": "completed"'
```

---

**版本：** v1.0  
**更新日期：** 2026-03-19  
**文档维护：** 调度中心项目组
