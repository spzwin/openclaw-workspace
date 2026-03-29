# Agent 提交通知 - 模板与示例

## 提交通知模板

每个专家 Agent 在完成任务后，**必须**向调度中心发送以下格式的通知：

```markdown
【任务完成通知】

项目编号：{project-id}
任务 ID：{task-id}
任务名称：{task-name}
执行 Agent：{expert-id}

完成情况：
- 状态：✅ 已完成 / ❌ 失败
- 成果路径：workspace/{project-id}/{output-path}
- 耗时：{duration}
- 备注：{notes}

请调度中心安排下一步工作。
```

## 完整示例

### 示例 1：任务成功完成

```markdown
【任务完成通知】

项目编号：demo-001
任务 ID：task-001
任务名称：产品需求分析
执行 Agent：product-manager

完成情况：
- 状态：✅ 已完成
- 成果路径：workspace/demo-001/deliverables/phase-1/prd.md
- 耗时：1.5 小时
- 备注：PRD 包含 15 个用户故事、32 个功能点、完整的验收标准。已同步到 context/ 目录供后续任务参考。

请调度中心安排下一步工作。
```

### 示例 2：任务执行失败

```markdown
【任务完成通知】

项目编号：demo-001
任务 ID：task-003
任务名称：前端开发
执行 Agent：engineering-frontend-developer

完成情况：
- 状态：❌ 失败
- 成果路径：workspace/demo-001/deliverables/phase-2/frontend/partial/
- 耗时：4 小时
- 备注：遇到技术阻塞：设计稿中的 3D 效果需要 Three.js 专业知识，超出我的能力范围。建议重新分配给 engineering-senior-developer 或添加 Three.js 专家。

请调度中心安排下一步工作。
```

### 示例 3：部分完成（可交付中间成果）

```markdown
【任务完成通知】

项目编号：demo-001
任务 ID：task-004
任务名称：后端开发
执行 Agent：engineering-backend-architect

完成情况：
- 状态：✅ 已完成（核心功能）
- 成果路径：workspace/demo-001/deliverables/phase-2/backend/
- 耗时：6 小时
- 备注：核心 API 已全部实现并通过单元测试。剩余 2 个边缘用例（占 10%）因依赖第三方服务暂未完成，不影响前端集成。建议标记为 80% 完成，继续下一步。

请调度中心安排下一步工作。
```

## 提交后的预期流程

### 1. 调度中心收到通知

```
[2026-03-19 10:30:00] INFO 收到完成通知：demo-001/task-001 by product-manager
```

### 2. 更新项目进度

`project.json` 更新为：

```json
{
  "progress": {
    "completedTasks": ["task-001"],
    "pendingTasks": ["task-002", "task-003", "task-004", "task-005", "task-006"],
    "percentComplete": 17
  },
  "currentAgent": null
}
```

### 3. 查找下一个任务

调度中心检查 `pipeline.json`：
- task-002 依赖 task-001 ✅
- task-002 可以开始

### 4. 派发下一个任务

调度中心向 `engineering-software-architect` 发送：

```markdown
【新任务派发】

项目编号：demo-001
任务 ID：task-002
任务名称：技术方案设计

上游依赖：
- task-001（产品需求分析）✅ 已完成
  成果：workspace/demo-001/deliverables/phase-1/prd.md

任务描述：
基于 PRD 设计系统架构，包含技术选型、模块划分、API 设计、数据库设计

输出要求：
- 路径：workspace/demo-001/deliverables/phase-1/architecture.md
- 格式：Markdown 文档 + 架构图

上下文：
- 项目文档：workspace/demo-001/context/
- 前置成果：workspace/demo-001/deliverables/phase-1/prd.md

请开始执行，完成后提交通知。
```

### 5. 更新当前 Agent 状态

```json
{
  "currentAgent": {
    "expertId": "engineering-software-architect",
    "agentId": "agent-xxx-xxx",
    "sessionKey": "session-yyy-yyy",
    "assignedAt": "2026-03-19T10:30:05Z",
    "task": "task-002"
  }
}
```

## 并行任务处理示例

当 task-002 完成后，task-003 和 task-004 可以**并行**执行：

### 调度中心同时派发两个任务

**派发给前端开发者：**
```markdown
【新任务派发】

项目编号：demo-001
任务 ID：task-003
任务名称：前端开发

上游依赖：
- task-002（技术方案设计）✅ 已完成
  成果：workspace/demo-001/deliverables/phase-1/architecture.md

...
```

**同时派发给后端开发者：**
```markdown
【新任务派发】

项目编号：demo-001
任务 ID：task-004
任务名称：后端开发

上游依赖：
- task-002（技术方案设计）✅ 已完成
  成果：workspace/demo-001/deliverables/phase-1/architecture.md

...
```

### project.json 更新

```json
{
  "currentAgent": [
    {
      "expertId": "engineering-frontend-developer",
      "task": "task-003",
      "assignedAt": "2026-03-19T14:00:00Z"
    },
    {
      "expertId": "engineering-backend-architect",
      "task": "task-004",
      "assignedAt": "2026-03-19T14:00:00Z"
    }
  ]
}
```

## 提交通知检查清单

在发送通知前，请确认：

- [ ] 成果已保存到正确路径
- [ ] 路径格式：`workspace/{project-id}/{output-path}`
- [ ] 通知包含所有必填字段
- [ ] 状态标记正确（✅ 或 ❌）
- [ ] 备注包含关键信息（阻塞、风险、建议）
- [ ] 已阅读 `README.md` 了解完整流程

## 常见错误

### ❌ 错误 1：忘记提交通知

**问题：** Agent 完成任务后没有提交通知，调度中心一直在等待。

**解决：** 立即补提交通知：

```markdown
【任务完成通知】（补交）

项目编号：demo-001
任务 ID：task-001
...
备注：抱歉忘记提交，现在补交。
```

### ❌ 错误 2：成果路径错误

**问题：** 路径写错，调度中心找不到成果文件。

**错误示例：**
```
成果路径：deliverables/prd.md  ❌
```

**正确示例：**
```
成果路径：workspace/demo-001/deliverables/phase-1/prd.md  ✅
```

### ❌ 错误 3：未说明失败原因

**问题：** 只标记失败，没有说明原因，调度中心无法处理。

**错误示例：**
```
- 状态：❌ 失败
- 备注：做不了
```

**正确示例：**
```
- 状态：❌ 失败
- 备注：需要访问内部数据库，但缺少权限。已联系 DBA，预计 2 小时后解决。建议暂停此任务或重新分配给有权限的 Agent。
```

---

**提示：** 复制上方模板，替换 `{}` 中的内容即可快速提交通知。
