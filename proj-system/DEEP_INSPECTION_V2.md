# 🔍 调度中心深度检查报告（第二轮）

**检查时间：** 2026-03-19 08:35  
**检查者：** 小爪 🐾  
**检查范围：** 中心调度执行规则 + Session 通道通知

---

## 一、核心问题发现

### 🔴 致命问题（立即修复）

| # | 问题 | 影响 | 状态 |
|---|------|------|------|
| 1 | **两个架构混用** | 调度逻辑混乱 | ⚠️ 待修复 |
| 2 | **Cron 路径错误** | 读取不存在的数据 | ✅ 已修复 |
| 3 | **Session 全为 pending** | 无法派发任何任务 | ⚠️ 待修复 |
| 4 | **专家 Agent 未创建** | 无实际执行者 | ⚠️ 待修复 |

---

## 二、架构混乱详情

### 现状：两套架构并存

```
架构 A（文档驱动 - 旧）:
路径：/Users/spzhong/.openclaw/agency-agents/proj-orchestrator/
状态：✅ 有实际项目数据 (PROJ-20260318-001)
      ✅ 有完整 sessions.json 模板
      ❌ Session 未初始化（全为 pending）
      ❌ 专家 Agent 未创建

架构 B（事件驱动 - 新）:
路径：/Users/spzhong/.openclaw/workspace/proj-system/
状态：✅ 有完整设计文档
      ✅ 有 TypeScript 代码框架
      ❌ 未实际部署
      ❌ 无项目数据
```

### Cron 配置问题

**原配置（错误）：**
```json
{
  "message": "读取 /Users/spzhong/.openclaw/workspace/proj-system/shared/cases/*/case.json"
}
```

**问题：**
- 该目录不存在
- `case.json` 格式不存在
- 与 `agency-agents/` 的数据完全不兼容

**修复后（正确）：**
```json
{
  "message": "读取 /Users/spzhong/.openclaw/agency-agents/proj-orchestrator/projects/*/meta.json"
}
```

---

## 三、Session 通道问题

### 当前状态

```json
{
  "proj-specialist": { "sessionId": "pending" },
  "proj-initial-bd": { "sessionId": "pending" },
  "proj-initial-research": { "sessionId": "pending" },
  "proj-mid-review": { "sessionId": "pending" },
  "proj-final-review": { "sessionId": "pending" }
}
```

### 问题分析

1. **从未创建过 Session**
   - `sessions/sessions.json` 为空
   - 没有调用过 `sessions_spawn`

2. **通道配置正确**
   - 所有专家都使用 `xg_cwork_im`
   - accountId 已配置

3. **需要初始化**
   - 为每个角色创建持久化 Session
   - 更新 sessions.json 中的 sessionId

---

## 四、项目状态检查

### PROJ-20260318-001

```json
{
  "status": "in_progress",
  "currentStage": "mid_review",
  "stages": {
    "created": { "done": true },
    "initial_review": { "done": true },
    "mid_review": { "done": false },
    "final_review": { "done": false }
  }
}
```

**已有成果：**
- ✅ BD 报告：`bd_report.md`
- ✅ 创研报告：`research_report.md`
- ⏳ 中评：待执行
- ⏳ 终评：待执行

**下一步：** 派发中评任务给 `proj-mid-review`

---

## 五、完整修复方案

### 阶段 1：立即修复（让系统运转）

#### 1.1 创建专家 Session

```javascript
// 为 5 个专家角色创建持久化 Session
const experts = [
  'proj-specialist',
  'proj-initial-bd',
  'proj-initial-research',
  'proj-mid-review',
  'proj-final-review'
];

for (const expert of experts) {
  const session = await sessions_spawn({
    task: `你是 ${expert} 专家。等待调度中心派发任务。`,
    label: expert,
    runtime: 'subagent',
    mode: 'session',
    cleanup: 'keep'
  });
  
  // 更新 sessions.json
  sessions[expert].sessionId = session.sessionKey;
  sessions[expert].lastContactAt = new Date().toISOString();
}
```

#### 1.2 测试消息发送

```javascript
// 发送测试消息到每个 Session
for (const [expertId, session] of Object.entries(sessions)) {
  await sessions_send({
    sessionKey: session.sessionId,
    message: `【系统测试】${expertId} 初始化完成`
  });
}
```

#### 1.3 派发中评任务

```javascript
// 当前项目处于 mid_review 阶段
await sessions_send({
  sessionKey: sessions['proj-mid-review'].sessionId,
  message: `【任务派发】
  
项目编号：PROJ-20260318-001
任务类型：中评
项目目录：/Users/spzhong/.openclaw/agency-agents/proj-orchestrator/projects/PROJ-20260318-001/

前置成果：
- BD 报告：bd_report.md
- 创研报告：research_report.md

请执行中期评审，输出评审报告到：RT03_Mid_Review/readme.md`
});
```

### 阶段 2：架构统一（长期方案）

#### 2.1 选择架构方向

**选项 A：继续使用文档驱动**
- 优点：已有数据，迁移成本低
- 缺点：轮询效率低

**选项 B：迁移到事件驱动**
- 优点：实时响应，架构先进
- 缺点：需要迁移数据，开发成本高

**建议：** 短期用 A，长期迁移到 B

#### 2.2 迁移路径

```
1. 保持架构 A 运行（不中断业务）
2. 并行开发架构 B
3. 在架构 B 中实现数据导入工具
4. 测试验证后切换
```

---

## 六、执行清单

### 立即执行（今天）

- [ ] 创建 5 个专家 Session
- [ ] 更新 sessions.json
- [ ] 测试消息发送
- [ ] 派发中评任务
- [ ] 验证完整流程

### 本周内

- [ ] 完善监控告警
- [ ] 添加错误重试
- [ ] 编写运维文档

### 下周

- [ ] 评估架构迁移方案
- [ ] 如迁移：制定详细计划
- [ ] 如不迁移：优化现有架构

---

## 七、风险点

### 高风险

1. **Session 创建失败**
   - 影响：无法派发任务
   - 缓解：手动创建 + 告警

2. **消息发送失败**
   - 影响：任务无法送达
   - 缓解：重试机制 + 降级

3. **数据不一致**
   - 影响：状态混乱
   - 缓解：定期校验 + 人工审计

### 中风险

1. **架构混用导致混淆**
   - 影响：开发效率低
   - 缓解：明确文档说明

2. **Cron 再次超时**
   - 影响：调度停滞
   - 缓解：监控 + 告警

---

## 八、监控指标

### 核心指标

| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| Cron 成功率 | >99% | 0% (13 连败) |
| Session 可用数 | 5/5 | 0/5 |
| 任务派发延迟 | <10s | N/A |
| 项目完成数 | - | 1 (已归档) |

### 告警阈值

- Cron 连续失败 3 次 → 告警
- Session 不可用 → 告警
- 项目卡住 >24h → 告警

---

## 九、总结

### 发现的问题

- 🔴 致命问题：**4 个**（1 个已修复，3 个待修复）
- 🟡 严重问题：**2 个**（架构混用、监控缺失）
- 🟢 一般问题：**3 个**（文档不全、测试不足、告警缺失）

### 修复进度

- ✅ 已完成：Cron 配置修复
- ⏳ 进行中：Session 初始化
- 📋 待开始：架构统一

### 建议行动

**立即执行：**
1. 创建 5 个专家 Session
2. 更新 sessions.json
3. 派发中评任务

**本周完成：**
1. 完善监控告警
2. 添加错误重试
3. 编写运维文档

**长期规划：**
1. 评估架构迁移
2. 制定迁移计划（如需要）

---

**报告完成时间：** 2026-03-19 08:40  
**状态：** 等待大爷确认修复方案 🐾
