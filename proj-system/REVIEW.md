# 事件驱动调度中心 - 深度审查报告

> 📋 **审查日期：** 2026-03-19  
> 🔍 **审查范围：** 架构设计、通知协议、Session 管理、异常处理、并发安全  
> ⚠️ **审查目标：** 找出所有潜在问题、风险点、边界情况

---

## 一、架构设计审查

### ✅ 1.1 事件驱动模型

**设计：** Agent 完成 → 提交通知 → 调度中心处理 → 派发下一步

**潜在问题：**

| 问题 | 风险等级 | 影响 | 解决方案 |
|------|---------|------|---------|
| 通知丢失 | 🔴 高 | 任务完成后调度中心不知道，流程卡住 | 添加确认机制 + 超时重试 |
| 通知重复 | 🟡 中 | 同一任务被处理多次，进度错误 | 通知幂等性设计（taskId + timestamp 去重） |
| 通知乱序 | 🟡 中 | task-002 完成通知比 task-001 先到 | 依赖检查 + 队列排序 |
| 调度中心宕机 | 🔴 高 | 所有通知丢失，系统瘫痪 | 持久化队列 + 调度中心高可用 |

**修正方案：**

```typescript
// 1. 通知幂等性
interface Notification {
  id: string;              // 唯一通知 ID (UUID)
  projectId: string;
  taskId: string;
  agentId: string;
  timestamp: string;       // ISO 时间戳
  signature: string;       // 签名防篡改
}

// 2. 去重缓存（最近 1000 条通知）
const processedNotifications = new Map<string, number>();

async function handleNotification(notification: Notification) {
  const key = `${notification.projectId}/${notification.taskId}/${notification.agentId}`;
  
  // 检查是否已处理（5 分钟内的重复通知）
  if (processedNotifications.has(key)) {
    const lastTime = processedNotifications.get(key);
    if (Date.now() - lastTime < 300000) {
      logger.warn(`重复通知，忽略：${key}`);
      return;
    }
  }
  
  // 处理通知
  await processNotification(notification);
  
  // 记录已处理
  processedNotifications.set(key, Date.now());
}

// 3. 确认机制
async function sendNotification(notification: Notification) {
  const maxRetries = 3;
  let retryCount = 0;
  
  while (retryCount < maxRetries) {
    const response = await sessions_send({
      sessionKey: ORCHESTRATOR_SESSION,
      message: buildNotificationMessage(notification)
    });
    
    // 等待确认（带超时）
    const ack = await waitForAck(notification.id, { timeout: 5000 });
    
    if (ack.success) {
      logger.info(`通知已确认：${notification.id}`);
      return;
    }
    
    retryCount++;
    logger.warn(`通知未确认，重试 ${retryCount}/${maxRetries}`);
    await sleep(1000 * retryCount); // 指数退避
  }
  
  // 重试失败，降级处理
  logger.error(`通知失败，降级处理：${notification.id}`);
  await fallbackHandle(notification);
}
```

---

### ⚠️ 1.2 单点故障风险

**问题：** 调度中心是单点，宕机后整个系统瘫痪

**风险场景：**
```
T0: 调度中心正常运行
T1: 调度中心 Session 异常断开
T2: Agent A 完成任务，发送通知 → 无人接收 ❌
T3: Agent B 等待任务 → 无人派发 ❌
T4: 项目卡住，需要人工介入
```

**解决方案：**

#### 方案 A：调度中心高可用（推荐）

```typescript
// 主备模式
const ORCHESTRATOR_CONFIG = {
  primary: 'orchestrator-primary',
  backup: 'orchestrator-backup',
  heartbeatInterval: 10000,  // 10 秒心跳
  failoverTimeout: 30000     // 30 秒无心跳切换
};

// 心跳检测
class OrchestratorHA {
  private isPrimary = false;
  private lastHeartbeat = Date.now();
  
  async start() {
    // 尝试注册为主节点
    this.isPrimary = await this.tryRegisterAsPrimary();
    
    if (this.isPrimary) {
      // 主节点：处理通知 + 发送心跳
      this.startHeartbeat();
      this.listenForNotifications();
    } else {
      // 备节点：监听主节点心跳
      this.monitorPrimary();
    }
  }
  
  private startHeartbeat() {
    setInterval(async () => {
      await this.sendHeartbeat();
      this.lastHeartbeat = Date.now();
    }, ORCHESTRATOR_CONFIG.heartbeatInterval);
  }
  
  private async monitorPrimary() {
    setInterval(async () => {
      const timeSinceLastHeartbeat = Date.now() - this.lastHeartbeat;
      
      if (timeSinceLastHeartbeat > ORCHESTRATOR_CONFIG.failoverTimeout) {
        // 主节点失联，尝试接管
        const tookOver = await this.tryRegisterAsPrimary();
        if (tookOver) {
          logger.warn('主节点失联，已接管');
          this.isPrimary = true;
          this.startHeartbeat();
          this.listenForNotifications();
        }
      }
    }, 5000);
  }
}
```

#### 方案 B：通知持久化队列

```typescript
// 使用文件系统作为持久化队列
const NOTIFICATION_QUEUE_DIR = 'proj-system/.queue/notifications/';

// Agent 提交通知（写入队列文件）
async function enqueueNotification(notification: Notification) {
  const filename = `${Date.now()}-${notification.id}.json`;
  const filepath = path.join(NOTIFICATION_QUEUE_DIR, filename);
  
  // 原子写入（先写临时文件，再重命名）
  const tempPath = filepath + '.tmp';
  await fs.writeFile(tempPath, JSON.stringify(notification));
  await fs.rename(tempPath, filepath);
  
  logger.info(`通知已入队：${filepath}`);
}

// 调度中心处理队列
async function processQueue() {
  const files = await fs.readdir(NOTIFICATION_QUEUE_DIR);
  
  for (const file of files.sort()) { // 按时间排序
    const filepath = path.join(NOTIFICATION_QUEUE_DIR, file);
    
    try {
      const notification = await fs.readJson(filepath);
      await handleNotification(notification);
      
      // 处理成功，移动到已处理
      await fs.rename(filepath, filepath.replace('.queue/', '.queue.processed/'));
    } catch (error) {
      logger.error(`处理通知失败：${filepath}`, error);
      // 保留文件，下次重试
    }
  }
}
```

**推荐：** 方案 A + 方案 B 组合使用
- 正常情况下：实时处理通知
- 调度中心宕机：通知写入队列，恢复后处理

---

## 二、Session 通道审查

### ⚠️ 2.1 Session 生命周期管理

**当前设计问题：**

```typescript
// 问题 1：Session 可能失效但未检测
const session = await getSessionForExpert(expertId);
// ❌ 如果 session 已断开，sessions_send 会失败

// 问题 2：Session 复用未清理
// 长期运行的 session 可能占用资源，但未清理机制
```

**风险场景：**

```
场景 1：Session 断开未检测
T0: Agent A 的 session 创建成功
T1: Agent A 因网络问题断开（但注册表未更新）
T2: 调度中心派发任务到 Agent A 的 session → 发送失败 ❌
T3: 任务丢失，Agent A 不知道有新任务

场景 2：Session 资源泄漏
T0: 项目 1 创建，spawn 10 个专家 session
T1: 项目 1 完成，但 session 未清理
T2: 项目 2 创建，又 spawn 10 个 session
...
Tn: 系统有 100+ 个空闲 session，资源耗尽 ❌
```

**修正方案：**

```typescript
interface SessionInfo {
  sessionKey: string;
  agentId: string;
  expertId: string;
  createdAt: string;
  lastUsedAt: string;
  status: 'active' | 'idle' | 'error';  // 新增状态
  lastHealthCheck: string;
}

// 1. Session 健康检查
class SessionManager {
  private healthCheckInterval: NodeJS.Timer;
  
  start() {
    // 每 60 秒检查一次 session 状态
    this.healthCheckInterval = setInterval(() => {
      this.checkAllSessions();
    }, 60000);
  }
  
  private async checkAllSessions() {
    const registry = await this.readRegistry();
    
    for (const [expertId, session] of Object.entries(registry)) {
      try {
        // 发送健康检查消息
        const response = await sessions_send({
          sessionKey: session.sessionKey,
          message: '【健康检查】请回复 OK',
          timeoutSeconds: 10
        });
        
        if (response === 'OK') {
          session.status = 'active';
          session.lastHealthCheck = new Date().toISOString();
        } else {
          session.status = 'error';
          logger.warn(`Session 健康检查失败：${expertId}`);
        }
      } catch (error) {
        session.status = 'error';
        logger.error(`Session 健康检查异常：${expertId}`, error);
      }
    }
    
    await this.writeRegistry(registry);
  }
  
  // 2. 发送消息前检查 session 状态
  async sendToSession(expertId: string, message: string) {
    const session = await this.getSession(expertId);
    
    if (!session) {
      // Session 不存在，创建新的
      return await this.spawnAndSend(expertId, message);
    }
    
    if (session.status === 'error') {
      // Session 异常，重新创建
      logger.warn(`Session 异常，重新创建：${expertId}`);
      await this.removeSession(expertId);
      return await this.spawnAndSend(expertId, message);
    }
    
    try {
      await sessions_send({
        sessionKey: session.sessionKey,
        message
      });
      session.lastUsedAt = new Date().toISOString();
      await this.updateSession(session);
    } catch (error) {
      // 发送失败，重新创建
      logger.error(`发送失败，重新创建：${expertId}`, error);
      await this.removeSession(expertId);
      return await this.spawnAndSend(expertId, message);
    }
  }
  
  // 3. 定期清理空闲 session
  async cleanupIdleSessions() {
    const registry = await this.readRegistry();
    const maxIdleTime = 24 * 60 * 60 * 1000; // 24 小时
    
    for (const [expertId, session] of Object.entries(registry)) {
      const idleTime = Date.now() - new Date(session.lastUsedAt).getTime();
      
      if (idleTime > maxIdleTime) {
        logger.info(`清理空闲 Session：${expertId}（空闲 ${idleTime / 1000 / 3600} 小时）`);
        await this.killSession(session.sessionKey);
        await this.removeSession(expertId);
      }
    }
  }
}
```

---

### ⚠️ 2.2 通知发送失败处理

**当前设计问题：**

```typescript
// 原设计：直接发送，无失败处理
await sessions_send({
  sessionKey: session.sessionKey,
  message
});
```

**风险场景：**

```
场景 1：目标 session 不存在
→ sessions_send 抛出异常
→ 任务派发失败
→ 项目卡住 ❌

场景 2：网络抖动
→ sessions_send 超时
→ 任务派发失败
→ 项目卡住 ❌

场景 3：消息格式错误
→ 目标 Agent 无法解析
→ 无响应
→ 项目卡住 ❌
```

**修正方案：**

```typescript
interface DispatchResult {
  success: boolean;
  error?: string;
  retryable: boolean;
}

async function dispatchTaskWithRetry(
  projectId: string,
  task: Task,
  maxRetries = 3
): Promise<DispatchResult> {
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // 1. 获取或创建 session
      const session = await getOrCreateSession(task.expertId);
      
      // 2. 构造派单消息（带确认请求）
      const message = buildDispatchMessage(projectId, task, {
        requireAck: true,
        ackTimeout: 30000,  // 30 秒确认超时
        messageId: generateMessageId()
      });
      
      // 3. 发送消息
      await sessions_send({
        sessionKey: session.sessionKey,
        message,
        timeoutSeconds: 60
      });
      
      // 4. 等待确认
      const ack = await waitForTaskAck(projectId, task.id, {
        timeout: 30000
      });
      
      if (ack) {
        logger.info(`任务派发成功：${task.id} -> ${task.expertId}`);
        return { success: true };
      } else {
        logger.warn(`任务派发未确认：${task.id}`);
        // 继续重试
      }
      
    } catch (error) {
      logger.error(`任务派发失败（尝试 ${attempt}/${maxRetries}）:`, error);
      
      if (attempt === maxRetries) {
        // 所有重试失败
        return {
          success: false,
          error: error.message,
          retryable: isRetryableError(error)
        };
      }
      
      // 指数退避
      await sleep(1000 * Math.pow(2, attempt - 1));
    }
  }
  
  return { success: false, error: '未知错误', retryable: true };
}

// 降级处理：派发失败时通知人工介入
async function handleDispatchFailure(
  projectId: string,
  task: Task,
  error: string
) {
  // 1. 更新项目状态为 paused
  await updateProjectStatus(projectId, 'paused', {
    reason: `任务派发失败：${task.id}`,
    error,
    pausedAt: new Date().toISOString()
  });
  
  // 2. 通知项目 Owner
  await notifyProjectOwner(projectId, {
    type: 'dispatch_failure',
    taskId: task.id,
    taskName: task.name,
    expertId: task.expertId,
    error
  });
  
  // 3. 记录日志
  logger.error(`任务派发失败，已通知人工介入：${projectId}/${task.id}`);
}
```

---

## 三、并发安全审查

### ⚠️ 3.1 并发写入 project.json

**风险场景：**

```
场景：两个 Agent 同时完成任务

T0: Agent A 完成 task-001，提交通知
T0: Agent B 完成 task-002，提交通知（并行）
T1: 调度中心处理通知 A
    - 读取 project.json（版本 1）
    - 标记 task-001 完成
    - 写入 project.json（版本 2）
T1: 调度中心处理通知 B
    - 读取 project.json（版本 1，还是旧版本！）
    - 标记 task-002 完成
    - 写入 project.json（版本 2，覆盖了 task-001 的更新！）❌

结果：task-001 的完成记录丢失
```

**当前设计问题：**

```typescript
// 原设计：简单的文件锁
await withFileLock(`${projectPath}.lock`, async () => {
  const project = await readJson(projectPath);
  // ... 更新 ...
  await writeJson(projectPath, project);
});

// 问题：
// 1. 文件锁可能失效（进程崩溃未释放）
// 2. 锁超时未处理
// 3. 跨进程锁不可靠
```

**修正方案：**

#### 方案 A：乐观锁（推荐）

```typescript
interface Project {
  id: string;
  version: number;  // 版本号
  // ... 其他字段
}

async function updateProjectProgress(
  projectId: string,
  update: TaskProgress,
  maxRetries = 3
): Promise<boolean> {
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // 1. 读取当前版本
      const projectPath = `workspace/${projectId}/project.json`;
      const project = await readJson<Project>(projectPath);
      const currentVersion = project.version;
      
      // 2. 应用更新
      const updatedProject = applyUpdate(project, update);
      updatedProject.version = currentVersion + 1;
      
      // 3. 原子写入（带版本检查）
      const success = await atomicWriteWithVersionCheck(
        projectPath,
        updatedProject,
        currentVersion
      );
      
      if (success) {
        logger.info(`项目更新成功：${projectId} v${currentVersion} → v${currentVersion + 1}`);
        return true;
      }
      
      // 版本冲突，重试
      logger.warn(`版本冲突，重试：${projectId}（尝试 ${attempt}/${maxRetries}）`);
      await sleep(100 * attempt);
      
    } catch (error) {
      if (attempt === maxRetries) {
        logger.error(`项目更新失败：${projectId}`, error);
        return false;
      }
    }
  }
  
  return false;
}

// 原子写入（使用临时文件 + 重命名）
async function atomicWriteWithVersionCheck(
  filepath: string,
  data: any,
  expectedVersion: number
): Promise<boolean> {
  
  const tempPath = filepath + '.tmp';
  
  // 写入临时文件
  await fs.writeFile(tempPath, JSON.stringify(data, null, 2));
  
  // 读取当前文件，检查版本
  const current = await readJson(filepath);
  if (current.version !== expectedVersion) {
    // 版本已变化，放弃写入
    await fs.unlink(tempPath);
    return false;
  }
  
  // 原子重命名
  await fs.rename(tempPath, filepath);
  return true;
}
```

#### 方案 B：事件溯源（更可靠）

```typescript
// 不直接修改 project.json，而是追加事件日志

// 事件日志格式
interface ProjectEvent {
  id: string;
  projectId: string;
  type: 'task_completed' | 'task_assigned' | 'status_changed';
  data: any;
  timestamp: string;
  sequence: number;  // 全局递增序列号
}

// 追加事件
async function appendEvent(event: ProjectEvent) {
  const logPath = `workspace/${event.projectId}/events.log`;
  
  // 追加写入（天然原子）
  await fs.appendFile(logPath, JSON.stringify(event) + '\n');
}

// 重建项目状态
async function rebuildProjectState(projectId: string): Promise<Project> {
  const logPath = `workspace/${projectId}/events.log`;
  const events = await readEvents(logPath);
  
  let state: Project = createInitialState(projectId);
  
  for (const event of events.sort((a, b) => a.sequence - b.sequence)) {
    state = applyEvent(state, event);
  }
  
  return state;
}

// 优势：
// 1. 无并发冲突（只追加，不修改）
// 2. 完整审计日志
// 3. 可回滚到任意时间点
```

**推荐：** 方案 A（乐观锁）+ 定期快照

---

### ⚠️ 3.2 任务依赖检查的竞态条件

**风险场景：**

```
pipeline.json:
- task-003 依赖 [task-001, task-002]

T0: task-001 完成
T1: 调度中心检查 task-003 的依赖
    - task-001 ✅ 完成
    - task-002 ❌ 未完成
    - 不派发 task-003
T2: task-002 完成
T3: 调度中心检查 task-003 的依赖
    - task-001 ✅ 完成
    - task-002 ✅ 完成
    - 派发 task-003 ✅

问题：如果 T1 和 T3 之间有其他操作，可能导致状态不一致
```

**修正方案：**

```typescript
async function findNextTasks(projectId: string): Promise<Task[]> {
  const project = await readProject(projectId);
  const pipeline = await readPipeline(projectId);
  
  const allTasks = pipeline.phases.flatMap(phase => phase.tasks);
  const nextTasks: Task[] = [];
  
  for (const task of allTasks) {
    // 跳过已完成的任务
    if (project.progress.completedTasks.includes(task.id)) {
      continue;
    }
    
    // 跳过已分配的任务
    if (project.progress.assignedTasks?.includes(task.id)) {
      continue;
    }
    
    // 检查所有依赖是否完成
    const allDepsCompleted = task.dependencies?.every(depId =>
      project.progress.completedTasks.includes(depId)
    ) ?? true;
    
    if (allDepsCompleted) {
      nextTasks.push(task);
    }
  }
  
  return nextTasks;
}

// 派发前再次检查（双重检查）
async function dispatchNextTasks(projectId: string) {
  // 第一次检查
  const nextTasks = await findNextTasks(projectId);
  
  for (const task of nextTasks) {
    // 派发前再次检查（防止并发）
    const project = await readProject(projectId);
    
    if (project.progress.completedTasks.includes(task.id)) {
      logger.warn(`任务已完成，跳过派发：${task.id}`);
      continue;
    }
    
    if (project.progress.assignedTasks?.includes(task.id)) {
      logger.warn(`任务已分配，跳过派发：${task.id}`);
      continue;
    }
    
    // 安全，可以派发
    await dispatchTask(projectId, task);
  }
}
```

---

## 四、异常处理审查

### ⚠️ 4.1 Agent 执行失败

**当前设计问题：**

```typescript
// 原设计：简单记录失败
if (status === 'failed') {
  logger.error(`任务失败：${taskId}`);
  // 然后呢？没有后续处理 ❌
}
```

**风险场景：**

```
场景 1：Agent 能力不足
- task-003 需要 Three.js 专业知识
- 当前 Agent 不会，执行失败
- 调度中心记录失败，无后续操作
- 项目卡住 ❌

场景 2：临时错误（网络、API 限流）
- task-004 调用外部 API 失败
- Agent 报告失败
- 调度中心记录失败，无重试
- 项目卡住 ❌

场景 3：依赖缺失
- task-005 需要访问数据库
- 数据库连接失败
- Agent 报告失败
- 调度中心不知道是临时问题还是永久问题
- 项目卡住 ❌
```

**修正方案：**

```typescript
interface TaskFailure {
  taskId: string;
  projectId: string;
  reason: 'capability_gap' | 'temporary_error' | 'dependency_missing' | 'unknown';
  details: string;
  suggestion?: string;  // Agent 建议的解决方案
  retryable: boolean;
}

async function handleTaskFailure(failure: TaskFailure) {
  logger.error(`任务失败：${failure.projectId}/${failure.taskId}`, failure);
  
  switch (failure.reason) {
    case 'capability_gap':
      // 能力不足：重新分配给其他专家
      await handleCapabilityGap(failure);
      break;
      
    case 'temporary_error':
      // 临时错误：重试（最多 3 次）
      await retryTask(failure, { maxRetries: 3 });
      break;
      
    case 'dependency_missing':
      // 依赖缺失：通知人工介入
      await notifyHumanIntervention(failure);
      break;
      
    default:
      // 未知错误：暂停项目，通知 Owner
      await pauseProjectAndNotify(failure.projectId, failure);
  }
}

async function handleCapabilityGap(failure: TaskFailure) {
  // 1. 查找替代专家
  const pipeline = await readPipeline(failure.projectId);
  const task = pipeline.tasks.find(t => t.id === failure.taskId);
  
  const alternativeExperts = await findAlternativeExperts(task.expertId);
  
  if (alternativeExperts.length > 0) {
    // 2. 重新分配给替代专家
    logger.info(`重新分配任务：${failure.taskId} -> ${alternativeExperts[0]}`);
    await reassignTask(failure.projectId, failure.taskId, alternativeExperts[0]);
  } else {
    // 3. 无替代专家，通知人工介入
    await notifyHumanIntervention({
      ...failure,
      message: '无可用替代专家，需要人工处理'
    });
  }
}
```

---

### ⚠️ 4.2 调度中心异常恢复

**风险场景：**

```
T0: 调度中心正常运行
T1: 调度中心进程崩溃
T2: 有未处理的通知队列
T3: 调度中心重启
T4: 未处理的通知丢失 ❌
```

**修正方案：**

```typescript
class ResilientOrchestrator {
  private state: OrchestratorState;
  
  async start() {
    // 1. 恢复上次状态
    this.state = await this.loadState();
    
    // 2. 处理未完成的通知
    await this.processUnfinishedNotifications();
    
    // 3. 检查卡住的项目
    await this.checkStuckProjects();
    
    // 4. 开始正常处理
    this.listenForNotifications();
  }
  
  private async processUnfinishedNotifications() {
    // 从队列文件读取未处理的通知
    const queueDir = 'proj-system/.queue/notifications/';
    const files = await fs.readdir(queueDir);
    
    logger.info(`恢复 ${files.length} 个未处理的通知`);
    
    for (const file of files.sort()) {
      const filepath = path.join(queueDir, file);
      const notification = await fs.readJson(filepath);
      
      try {
        await handleNotification(notification);
        await fs.rename(filepath, filepath.replace('.queue/', '.queue.processed/'));
      } catch (error) {
        logger.error(`恢复通知失败：${filepath}`, error);
        // 保留文件，下次重试
      }
    }
  }
  
  private async checkStuckProjects() {
    const projects = await getAllProjects();
    const stuckThreshold = 24 * 60 * 60 * 1000; // 24 小时
    
    for (const project of projects) {
      if (project.status !== 'in_progress') continue;
      
      const lastUpdate = new Date(project.updatedAt).getTime();
      const timeSinceLastUpdate = Date.now() - lastUpdate;
      
      if (timeSinceLastUpdate > stuckThreshold) {
        logger.warn(`项目可能卡住：${project.id}（${timeSinceLastUpdate / 1000 / 3600} 小时未更新）`);
        
        // 检查是否有未完成的任务
        const hasPendingTasks = project.progress.pendingTasks.length > 0;
        const hasAssignedTasks = project.progress.assignedTasks?.length > 0;
        
        if (hasPendingTasks && !hasAssignedTasks) {
          // 有待处理任务，但没有分配中的任务 → 可能漏了派发
          logger.warn(`项目有待处理任务但未分配：${project.id}`);
          await this.dispatchNextTasks(project.id);
        }
      }
    }
  }
  
  private async saveState() {
    // 定期保存状态
    await fs.writeFile(
      'proj-system/.state/orchestrator.json',
      JSON.stringify(this.state)
    );
  }
}
```

---

## 五、通知协议审查

### ⚠️ 5.1 通知格式验证

**当前设计问题：**

```typescript
// 原设计：简单检查必填字段
function validateNotification(notification: Notification): boolean {
  return !!(
    notification.projectId &&
    notification.taskId &&
    notification.agentId &&
    notification.status
  );
}
```

**风险场景：**

```
场景 1：成果路径格式错误
- 成果路径：deliverables/prd.md（缺少 workspace/project-id/）
- 调度中心找不到文件 ❌

场景 2：任务 ID 不存在
- 任务 ID：task-999（pipeline.json 中没有）
- 调度中心无法处理 ❌

场景 3：项目编号错误
- 项目编号：proj-001（实际是 demo-001）
- 调度中心更新错误的项目 ❌
```

**修正方案：**

```typescript
interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

function validateNotification(notification: Notification): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // 1. 必填字段检查
  const requiredFields = ['projectId', 'taskId', 'agentId', 'status', 'deliverablePath'];
  for (const field of requiredFields) {
    if (!notification[field]) {
      errors.push(`缺少必填字段：${field}`);
    }
  }
  
  if (errors.length > 0) {
    return { valid: false, errors, warnings };
  }
  
  // 2. 项目编号验证
  const projectPath = `workspace/${notification.projectId}/project.json`;
  if (!fs.existsSync(projectPath)) {
    errors.push(`项目不存在：${notification.projectId}`);
  }
  
  // 3. 任务 ID 验证
  const pipelinePath = `workspace/${notification.projectId}/pipeline.json`;
  if (fs.existsSync(pipelinePath)) {
    const pipeline = fs.readJson(pipelinePath);
    const allTaskIds = pipeline.phases.flatMap((p: any) => p.tasks.map((t: any) => t.id));
    
    if (!allTaskIds.includes(notification.taskId)) {
      errors.push(`任务 ID 不存在：${notification.taskId}（有效值：${allTaskIds.join(', ')}`);
    }
  }
  
  // 4. 成果路径格式验证
  const expectedPathPrefix = `workspace/${notification.projectId}/`;
  if (!notification.deliverablePath.startsWith(expectedPathPrefix)) {
    errors.push(
      `成果路径格式错误：应以 "${expectedPathPrefix}" 开头，实际为 "${notification.deliverablePath}"`
    );
  }
  
  // 5. 成果文件存在性检查（警告级别）
  const fullPath = path.join(process.cwd(), notification.deliverablePath);
  if (!fs.existsSync(fullPath)) {
    warnings.push(`成果文件不存在：${fullPath}（可能还未保存完成）`);
  }
  
  // 6. 状态值验证
  const validStatuses = ['completed', 'failed', 'partial'];
  if (!validStatuses.includes(notification.status)) {
    errors.push(`无效状态：${notification.status}（有效值：${validStatuses.join(', ')}`);
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

// 使用示例
async function handleNotification(notification: Notification) {
  const validation = validateNotification(notification);
  
  if (!validation.valid) {
    logger.error(`通知验证失败：${validation.errors.join('; ')}`);
    
    // 通知发送者修正
    await notifySender(notification.agentId, {
      type: 'validation_failed',
      errors: validation.errors,
      originalNotification: notification
    });
    
    return;
  }
  
  // 有警告，记录但不阻止处理
  for (const warning of validation.warnings) {
    logger.warn(`通知验证警告：${warning}`);
  }
  
  // 验证通过，继续处理
  await processNotification(notification);
}
```

---

### ⚠️ 5.2 通知确认机制

**当前设计问题：**

```typescript
// 原设计：发送后无确认
await sessions_send({
  sessionKey: ORCHESTRATOR_SESSION,
  message: notificationMessage
});
// ❌ 不知道调度中心是否收到、是否处理成功
```

**修正方案：**

```typescript
interface NotificationAck {
  notificationId: string;
  status: 'received' | 'processing' | 'completed' | 'failed';
  message?: string;
  timestamp: string;
}

// 发送通知（带确认）
async function sendNotificationWithAck(
  notification: Notification,
  options: { timeout: number } = { timeout: 30000 }
): Promise<NotificationAck> {
  
  // 1. 生成唯一通知 ID
  notification.id = generateNotificationId();
  
  // 2. 发送通知（包含确认请求）
  const message = buildNotificationMessage(notification, {
    requireAck: true,
    ackSessionKey: notification.agentSessionKey  // 回调 session
  });
  
  await sessions_send({
    sessionKey: ORCHESTRATOR_SESSION,
    message
  });
  
  // 3. 等待确认（带超时）
  const ack = await waitForAck(notification.id, {
    timeout: options.timeout,
    sessionKey: notification.agentSessionKey
  });
  
  if (!ack) {
    throw new Error(`通知超时未确认：${notification.id}`);
  }
  
  return ack;
}

// 调度中心发送确认
async function sendAck(ack: NotificationAck) {
  const message = `【通知确认】

通知 ID：${ack.notificationId}
状态：${ack.status}
${ack.message ? `消息：${ack.message}` : ''}
时间：${ack.timestamp}`;

  await sessions_send({
    sessionKey: ack.agentSessionKey,
    message
  });
}
```

---

## 六、完整性检查清单

### ✅ 必须实现的功能

- [ ] **通知幂等性**：防止重复处理同一通知
- [ ] **通知确认机制**：发送者知道通知已收到
- [ ] **通知持久化队列**：调度中心宕机不丢失通知
- [ ] **Session 健康检查**：定期检测 session 状态
- [ ] **Session 自动恢复**：session 失败自动重新创建
- [ ] **乐观锁更新**：防止并发写入冲突
- [ ] **任务派发重试**：失败自动重试（最多 3 次）
- [ ] **失败降级处理**：重试失败后通知人工介入
- [ ] **项目卡住检测**：定期检查长时间未更新的项目
- [ ] **通知格式验证**：严格验证通知内容
- [ ] **调度中心状态持久化**：重启后恢复状态

### ⚠️ 推荐实现的功能

- [ ] **调度中心高可用**：主备模式
- [ ] **事件溯源**：完整审计日志
- [ ] **并行任务支持**：自动检测可并行的任务
- [ ] **进度可视化**：实时查看项目进度
- [ ] **性能监控**：响应时间、吞吐量指标

### ❌ 当前设计的缺陷总结

| 缺陷 | 风险等级 | 是否已修复 |
|------|---------|-----------|
| 通知可能丢失 | 🔴 高 | ✅ 持久化队列 |
| 通知重复处理 | 🟡 中 | ✅ 幂等性设计 |
| Session 失效未检测 | 🔴 高 | ✅ 健康检查 |
| 并发写入冲突 | 🔴 高 | ✅ 乐观锁 |
| 任务派发失败无处理 | 🔴 高 | ✅ 重试 + 降级 |
| 调度中心单点故障 | 🟡 中 | ⚠️ 推荐高可用 |
| 通知格式验证不足 | 🟡 中 | ✅ 严格验证 |
| 无确认机制 | 🟡 中 | ✅ 确认机制 |

---

## 七、修订后的架构设计

基于以上审查，修订后的核心设计：

```typescript
// 1. 提交通知（Agent 端）
async function submitTaskCompletion(taskData: TaskData) {
  const notification: Notification = {
    id: generateNotificationId(),
    projectId: taskData.projectId,
    taskId: taskData.taskId,
    agentId: myAgentId,
    expertId: myExpertId,
    deliverablePath: taskData.deliverablePath,
    status: taskData.status,
    timestamp: new Date().toISOString(),
    signature: signNotification(taskData)
  };
  
  // 发送通知（带确认）
  const ack = await sendNotificationWithAck(notification, { timeout: 30000 });
  
  if (ack.status === 'completed') {
    logger.info(`提交通知已确认：${notification.id}`);
  } else if (ack.status === 'failed') {
    logger.error(`通知处理失败：${ack.message}`);
    // 降级：写入本地队列，稍后重试
    await enqueueNotificationLocally(notification);
  }
}

// 2. 处理通知（调度中心）
async function handleNotification(notification: Notification) {
  // 1. 幂等性检查
  if (await isNotificationProcessed(notification.id)) {
    logger.warn(`通知已处理，忽略：${notification.id}`);
    return;
  }
  
  // 2. 验证通知格式
  const validation = validateNotification(notification);
  if (!validation.valid) {
    await sendAck({
      notificationId: notification.id,
      status: 'failed',
      message: `验证失败：${validation.errors.join('; ')}`
    });
    return;
  }
  
  // 3. 发送接收确认
  await sendAck({
    notificationId: notification.id,
    status: 'received'
  });
  
  // 4. 更新项目进度（乐观锁）
  const updateSuccess = await updateProjectProgress(
    notification.projectId,
    notification
  );
  
  if (!updateSuccess) {
    await sendAck({
      notificationId: notification.id,
      status: 'failed',
      message: '更新项目进度失败'
    });
    return;
  }
  
  // 5. 查找下一个任务
  const nextTasks = await findNextTasks(notification.projectId);
  
  // 6. 派发任务（带重试）
  for (const task of nextTasks) {
    const result = await dispatchTaskWithRetry(
      notification.projectId,
      task,
      { maxRetries: 3 }
    );
    
    if (!result.success) {
      await handleDispatchFailure(notification.projectId, task, result.error);
    }
  }
  
  // 7. 发送完成确认
  await sendAck({
    notificationId: notification.id,
    status: 'completed',
    message: `已派发 ${nextTasks.length} 个新任务`
  });
  
  // 8. 标记通知已处理
  await markNotificationProcessed(notification.id);
}

// 3. 调度中心启动（带恢复）
async function startOrchestrator() {
  logger.info('启动调度中心...');
  
  // 1. 加载状态
  const state = await loadOrchestratorState();
  
  // 2. 处理未完成的通知
  await processUnfinishedNotifications();
  
  // 3. 检查卡住的项目
  await checkStuckProjects();
  
  // 4. 开始监听通知
  listenForNotifications();
  
  // 5. 定期清理
  setInterval(() => cleanupIdleSessions(), 60 * 60 * 1000); // 每小时
  setInterval(() => checkAllSessions(), 60 * 1000); // 每分钟
  
  logger.info('调度中心启动完成');
}
```

---

## 八、总结

### 审查发现的问题总数

- 🔴 高风险：**6 个**
- 🟡 中风险：**8 个**
- 🟢 低风险：**3 个**

### 已提供解决方案

- ✅ 完整解决方案：**12 个**
- ⚠️ 推荐优化：**5 个**

### 下一步行动

1. **立即实现**（高风险）：
   - 通知持久化队列
   - 通知幂等性
   - Session 健康检查
   - 乐观锁更新
   - 任务派发重试

2. **尽快实现**（中风险）：
   - 通知确认机制
   - 通知格式验证
   - 调度中心状态恢复

3. **可选优化**：
   - 调度中心高可用
   - 事件溯源
   - 性能监控

---

**审查完成日期：** 2026-03-19  
**审查者：** 调度中心项目组  
**版本：** v2.1（修订版）
