# 调度中心初始化脚本

## 问题诊断

### 当前状态
- **Cron 调度器:** ✅ 已修复 (delivery.channel=webchat, timeout=90s)
- **Session 映射:** ❌ 所有 sessionId = "pending"
- **项目状态:** PROJ-20260318-001 → `in_progress`, `mid_review` 阶段

### 根本原因
1. **两个架构混用**
   - `proj-system/` - 事件驱动架构（新）
   - `agency-agents/proj-orchestrator/` - 文档驱动架构（旧）
   
2. **Session 未初始化**
   - sessions.json 中所有 sessionId = "pending"
   - 从未实际创建过 Agent Session

3. **Cron 路径错误**
   - 原配置指向 `workspace/proj-system/shared/cases/`（不存在）
   - 正确路径应为 `agency-agents/proj-orchestrator/projects/`

---

## 修复方案

### 方案 A：统一使用文档驱动架构（推荐）

**理由：**
- `agency-agents/proj-orchestrator/` 已有完整的项目结构
- PROJ-20260318-001 已有实际数据（BD 报告、创研报告）
- 只需初始化 Session 即可开始工作

**步骤：**

1. **初始化 Session**
   ```
   为每个专家角色创建持久化 Session：
   - proj-specialist
   - proj-initial-bd
   - proj-initial-research
   - proj-mid-review
   - proj-final-review
   ```

2. **更新 sessions.json**
   ```json
   {
     "sessionId": "实际的 sessionKey",
     "lastContactAt": "2026-03-19T08:30:00+08:00"
   }
   ```

3. **测试任务派发**
   - 发送消息到每个 Session
   - 确认消息送达

### 方案 B：迁移到事件驱动架构

**理由：**
- 更现代的设计
- 实时响应
- 更好的扩展性

**步骤：**
1. 迁移现有项目数据到 `proj-system/workspace/`
2. 部署新调度中心代码
3. 配置事件监听

---

## 立即执行（方案 A）

### 1. 创建初始化脚本

```bash
# 为每个专家角色创建 Session
# 更新 sessions.json 中的 sessionId
```

### 2. 验证流程

```
Cron 触发 → 读取 meta.json → 检查状态 → 查找下一步 → 发送任务
```

---

## 待确认事项

1. **架构选择：** 继续使用文档驱动（方案 A）还是迁移到事件驱动（方案 B）？
2. **Session 创建：** 需要为 5 个专家角色创建持久化 Session
3. **消息通道：** 所有专家都使用 `xg_cwork_im` 通道

---

**建议：** 先执行方案 A 让系统运转起来，同时并行开发方案 B 作为长期方案。
