# 快速开始指南

> 🐾 5 分钟启动你的第一个多 Agent 项目！

---

## 📋 前置检查

```bash
# 1. 检查目录结构
ls -la proj-system/orchestrator/
# 应看到：index.ts, session-manager.ts, notification-queue.ts, project-manager.ts, agent-status-manager.ts

# 2. 检查示例项目
ls -la workspace/PROJ-20260319-001/
# 应看到：meta.json, pipeline.json, RT01_*, RT02_*, RT03_*, RT04_*
```

---

## 🚀 步骤 1：初始化新项目

```bash
# 使用默认配置创建项目
cd /Users/spzhong/.openclaw/workspace/proj-system
./scripts/init-project.sh

# 或自定义项目名称
./scripts/init-project.sh "PROJ-20260319-002" "电商数据分析平台"
```

**输出示例：**
```
🚀 初始化项目：PROJ-20260319-002
   名称：电商数据分析平台
   路径：/Users/spzhong/.openclaw/workspace/workspace/PROJ-20260319-002
📁 复制项目模板...
📝 更新项目元数据...
📋 更新 Pipeline...
🔄 更新 Agent 状态文件...
📜 创建历史日志...
🤖 初始化 Agent 目录...
   创建 Agent 状态：expert-bd
   创建 Agent 状态：expert-research
   创建 Agent 状态：expert-mid-review
   创建 Agent 状态：expert-final-review

✅ 项目初始化完成！
```

---

## 🚀 步骤 2：创建专家 Agent 配置

为每个专家创建 SOUL.md 等配置文件：

```bash
# 创建 BD 专家
mkdir -p proj-system/agents/expert-bd
cat > proj-system/agents/expert-bd/SOUL.md << 'EOF'
# expert-bd - BD 初审专家

## 职责
- 分析客户需求
- 确认项目范围、预算、时间线
- 输出需求文档（bd_report.md）

## RT 机制
- 工作目录：workspace/{projectId}/RT01_BD_Analysis/
- 状态文件：RT01_BD_Analysis/agent-status.json
- 交付物：RT01_BD_Analysis/deliverables/bd_report.md

## 工作流程
1. 接收任务通知
2. 更新 agent-status.json 为 working
3. 调研、分析、撰写
4. 完成 bd_report.md
5. 更新状态为 completed
6. 提交通知到调度中心
EOF

# 类似创建其他专家...
# expert-research (RT02)
# expert-mid-review (RT03)
# expert-final-review (RT04)
```

---

## 🚀 步骤 3：启动调度中心

```bash
# 如果有 Node.js 环境
cd proj-system
npm install  # 首次运行
npm start    # 启动调度中心
```

**或手动测试流程：**

```bash
# 1. 查看当前项目状态
cat workspace/PROJ-20260319-001/meta.json

# 2. 手动派发 RT01 任务
# （实际由调度中心自动派发，这里模拟）
echo "派发 RT01 给 expert-bd..."

# 3. 模拟 Agent 开始工作
cat > workspace/PROJ-20260319-001/RT01_BD_Analysis/agent-status.json << 'EOF'
{
  "projectId": "PROJ-20260319-001",
  "expertId": "expert-bd",
  "rtDirectory": "RT01_BD_Analysis",
  "phase": "working",
  "drafts": ["drafts/v1.md"],
  "research": [],
  "deliverables": [],
  "log": [
    {"timestamp": "2026-03-19T08:35:00Z", "action": "task_received"},
    {"timestamp": "2026-03-19T08:36:00Z", "action": "started_work"}
  ],
  "updatedAt": "2026-03-19T08:36:00Z"
}
EOF

# 4. 模拟完成工作
mkdir -p workspace/PROJ-20260319-001/RT01_BD_Analysis/deliverables
cat > workspace/PROJ-20260319-001/RT01_BD_Analysis/deliverables/bd_report.md << 'EOF'
# BD 分析报告

## 客户需求
- ...

## 项目范围
- ...

## 预算评估
- ...

## 时间线
- ...
EOF

# 5. 更新状态为完成
cat > workspace/PROJ-20260319-001/RT01_BD_Analysis/agent-status.json << 'EOF'
{
  "projectId": "PROJ-20260319-001",
  "expertId": "expert-bd",
  "rtDirectory": "RT01_BD_Analysis",
  "phase": "completed",
  "drafts": ["drafts/v1.md"],
  "research": [],
  "deliverables": ["deliverables/bd_report.md"],
  "log": [
    {"timestamp": "2026-03-19T08:35:00Z", "action": "task_received"},
    {"timestamp": "2026-03-19T08:36:00Z", "action": "started_work"},
    {"timestamp": "2026-03-19T08:45:00Z", "action": "completed"}
  ],
  "updatedAt": "2026-03-19T08:45:00Z"
}
EOF

# 6. 提交通知（模拟调度中心处理）
# 实际应调用 enqueueNotification()
echo "提交通知：RT01 完成"

# 7. 检查项目状态更新
cat workspace/PROJ-20260319-001/meta.json
# 应看到 completedTasks: ["RT01"], version: 2
```

---

## 🚀 步骤 4：验证流程

```bash
# 检查项目进度
cat workspace/PROJ-20260319-001/meta.json | jq '.progress'

# 检查历史日志
cat workspace/PROJ-20260319-001/history.log

# 检查 Agent 状态
cat proj-system/agents/expert-bd/status.json

# 检查通知队列
ls -la proj-system/.queue/completed/
```

---

## 📊 核心机制验证

### 1. 通知队列
```bash
# 查看队列状态
ls proj-system/.queue/*/ | wc -l
# pending: 0, processing: 0, completed: 1, failed: 0
```

### 2. Session 健康检查
```bash
# 查看 Session 注册表
cat proj-system/.sessions.json
# 应看到 4 个专家的状态
```

### 3. 乐观锁
```bash
# 查看项目版本
cat workspace/PROJ-20260319-001/meta.json | jq '.version'
# 初始：1, RT01 完成后：2, RT02 完成后：3, ...
```

### 4. Agent 状态
```bash
# 查看 Agent 个人状态
cat proj-system/agents/expert-bd/status.json | jq '.currentTask'
# 查看 Agent 工作区状态
cat workspace/PROJ-20260319-001/RT01_BD_Analysis/agent-status.json
```

---

## 🎯 完整流程示意

```
T0:  项目创建 (version=1)
     └─ pendingTasks: [RT01, RT02, RT03, RT04]

T1:  派发 RT01, RT02 (并行)
     └─ assignedTasks: [RT01, RT02]

T2:  RT01 完成 (version=2)
     └─ completedTasks: [RT01]
     └─ assignedTasks: [RT02]

T3:  RT02 完成 (version=3)
     └─ completedTasks: [RT01, RT02]
     └─ 触发 RT03

T4:  派发 RT03
     └─ assignedTasks: [RT03]

T5:  RT03 完成 (version=4)
     └─ completedTasks: [RT01, RT02, RT03]
     └─ 触发 RT04

T6:  派发 RT04
     └─ assignedTasks: [RT04]

T7:  RT04 完成 (version=5)
     └─ completedTasks: [RT01, RT02, RT03, RT04]
     └─ status: completed ✅
```

---

## 🛠️ 故障排查

### 问题 1: 任务未派发
```bash
# 检查 pipeline.json 依赖配置
cat workspace/PROJ-*/pipeline.json | jq '.phases[].tasks[] | {id, dependencies}'

# 检查项目状态
cat workspace/PROJ-*/meta.json | jq '.progress'
```

### 问题 2: Agent 状态未更新
```bash
# 检查 agent-status.json 路径
ls workspace/PROJ-*/RT01_*/agent-status.json

# 检查 Agent 个人状态
cat proj-system/agents/expert-*/status.json
```

### 问题 3: 通知队列堆积
```bash
# 查看 pending 队列
ls proj-system/.queue/pending/

# 检查调度中心日志
cat proj-system/logs/orchestrator.log
```

---

## 📚 相关文档

- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - 详细实现指南
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 架构设计文档
- [REVIEW.md](./REVIEW.md) - 审查报告

---

**有问题？** 查看日志或联系调度中心项目组 🐾
