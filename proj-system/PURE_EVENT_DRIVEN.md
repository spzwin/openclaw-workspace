# 纯事件驱动架构（无定时任务）

> 📅 **更新日期：** 2026-03-19  
> 🎯 **原则：** 无任何定时轮询，所有操作由事件触发

---

## ❌ 已移除的定时任务

| 原定时任务 | 移除时间 | 替代方案 |
|-----------|---------|---------|
| Session 健康检查（60 秒） | v2.2 | 发送消息前检查 |
| 清理旧通知（1 小时） | v2.2 | 启动时清理 + 手动触发 |
| 清理空闲 Session（1 小时） | v2.2 | 启动时清理 + 手动触发 |
| 队列轮询（5 秒） | v2.2 | 通知到达时立即处理 |

---

## ✅ 纯事件驱动流程

### 核心流程

```
┌─────────────────────────────────────────────────────────────┐
│                     事件驱动调度中心                          │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
              ┌─────────────┴─────────────┐
              │                           │
    ┌─────────▼─────────┐     ┌──────────▼──────────┐
    │  Agent 提交通知    │     │  调度中心启动事件    │
    │  (外部事件)        │     │  (启动时一次性事件)  │
    └─────────┬─────────┘     └──────────┬──────────┘
              │                           │
              │                           ▼
              │              ┌────────────────────────┐
              │              │ 1. 初始化队列           │
              │              │ 2. 清理空闲 Session     │
              │              │ 3. 清理旧通知           │
              │              │ 4. 恢复未完成通知       │
              │              └────────────────────────┘
              ▼
    ┌─────────────────────────────────────────────────┐
    │  提交通知（enqueueNotification）                 │
    │  → 写入队列文件（持久化）                         │
    │  → 立即处理（handleNotification）                 │
    └─────────────────────────────────────────────────┘
                            │
                            ▼
    ┌─────────────────────────────────────────────────┐
    │  处理通知（handleNotification）                   │
    │  1. 验证通知格式                                 │
    │  2. 更新项目进度（乐观锁）                        │
    │  3. 更新 Agent 状态                               │
    │  4. 查找下一个任务                               │
    │  5. 派发任务（带重试）                           │
    └─────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │ 派发成功         │         │ 派发失败         │
    │ → 等待下一个通知 │         │ → 写入失败队列   │
    │                 │         │ → 通知人工介入   │
    └─────────────────┘         └─────────────────┘
```

---

## 🔍 事件触发点

### 1. Agent 提交通知（主要事件源）

```typescript
// Agent 完成工作后调用
await enqueueNotification({
  projectId: 'PROJ-001',
  taskId: 'RT01',
  expertId: 'expert-bd',
  deliverablePath: 'workspace/PROJ-001/RT01_BD_Analysis/deliverables/bd_report.md',
  status: 'completed',
  timestamp: new Date().toISOString()
});

// enqueueNotification 内部：
// 1. 写入队列文件（持久化）
// 2. 立即调用 handleNotification
```

### 2. 调度中心启动（一次性事件）

```typescript
await startOrchestrator();
// 启动时执行：
// 1. 初始化队列
// 2. 清理空闲 Session（一次性）
// 3. 清理旧通知（一次性）
// 4. 恢复未完成的通知
// 5. 开始监听新通知
```

### 3. 发送消息前健康检查（按需触发）

```typescript
// 派发任务时调用
async function sendToSession(expertId: string, message: string) {
  const session = await this.getOrCreateSession(expertId);
  
  // 发送前检查（仅当 session 状态异常时）
  if (session.status !== 'active' && session.status !== 'idle') {
    // 重新创建 Session
    await this.removeSession(expertId);
    const newSession = await this.createSession(expertId);
    return await this.doSend(newSession.sessionKey, message);
  }
  
  // 发送消息
  await this.doSend(session.sessionKey, message);
}
```

---

## 📊 对比：定时轮询 vs 事件驱动

| 维度 | 定时轮询（旧） | 事件驱动（新） |
|------|--------------|---------------|
| **资源消耗** | 持续轮询，浪费 CPU | 仅在事件到达时处理 |
| **响应延迟** | 最多等待轮询间隔 | 立即处理 |
| **实现复杂度** | 需要管理定时器 | 简单直接 |
| **可靠性** | 轮询间隔内可能丢失事件 | 队列持久化，不丢失 |
| **可扩展性** | 轮询频率固定，难以弹性 | 事件驱动，天然弹性 |

---

## 🛠️ 手动触发工具

虽然移除了定时任务，但提供手动触发工具：

### 清理空闲 Session

```bash
# 调用 sessionManager.cleanupIdleSessions()
# 场景：想立即清理，不想等到下次启动
```

### 清理旧通知

```bash
# 调用 cleanupOldNotifications(24)
# 场景：队列目录占用过大，手动清理
```

### 处理积压队列

```bash
# 调用 processQueue(handleNotification)
# 场景：调度中心重启后，手动触发队列处理
```

---

## 📋 检查清单

### 代码审查
- [x] 移除 `setInterval` 定时器
- [x] Session 健康检查改为发送前检查
- [x] 清理任务改为启动时一次性执行
- [x] 队列处理改为事件触发

### 文档更新
- [x] PURE_EVENT_DRIVEN.md（本文档）
- [x] 更新 session-manager.ts 注释
- [x] 更新 index.ts 注释
- [x] 更新 IMPLEMENTATION_GUIDE.md

---

## 🎯 事件流示例

### 完整流程（RT01→RT04）

```
T0:  调度中心启动
     → 初始化队列
     → 清理空闲 Session（一次性）
     → 清理旧通知（一次性）
     → 等待通知

T1:  人工派发 RT01, RT02（并行）
     → 调用 dispatchTaskWithRetry()
     → 发送消息到 expert-bd, expert-research

T2:  expert-bd 完成 RT01
     → 调用 enqueueNotification(RT01)
     → 写入队列文件
     → 立即调用 handleNotification()
     → 更新项目进度（version 1→2）
     → 查找下一个任务（RT01✅, RT02⏳ → 无新任务）

T3:  expert-research 完成 RT02
     → 调用 enqueueNotification(RT02)
     → 写入队列文件
     → 立即调用 handleNotification()
     → 更新项目进度（version 2→3）
     → 查找下一个任务（RT01✅, RT02✅ → RT03 可执行）
     → 派发 RT03 给 expert-mid-review

T4:  expert-mid-review 完成 RT03
     → 调用 enqueueNotification(RT03)
     → 更新项目进度（version 3→4）
     → 派发 RT04 给 expert-final-review

T5:  expert-final-review 完成 RT04
     → 调用 enqueueNotification(RT04)
     → 更新项目进度（version 4→5）
     → 无新任务 → 项目完成 ✅
```

**全程无定时任务！** 所有操作由 Agent 提交通知触发。

---

## 🚀 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0 | 2026-03-19 | 初始事件驱动设计 |
| v2.1 | 2026-03-19 | 添加通知队列 + 乐观锁 |
| v2.2 | 2026-03-19 08:35 | **移除所有定时任务，纯事件驱动** |

---

**设计原则：** 事件驱动就应该是纯粹的事件驱动，没有任何定时轮询的阴影！🐾
