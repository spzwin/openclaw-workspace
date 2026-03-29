# 事件驱动调度中心 v2 - 文档索引

> 🎯 **核心改变：** 从定时器轮询 → 事件驱动
> 
> ✅ Agent 完成后主动通知 → 调度中心立即处理 → 派发下一步

## 📚 文档导航

### 🚀 快速开始

**新手必读！按顺序阅读：**

1. **[README.md](./README.md)** - 使用指南
   - 5 分钟快速上手
   - 创建第一个项目
   - 提交通知模板
   - 常见问题解答

2. **[SUBMIT_TEMPLATE.md](./SUBMIT_TEMPLATE.md)** - 提交通知模板
   - 通知格式详解
   - 完整示例
   - 检查清单
   - 常见错误

### 🏗️ 架构设计

**深入理解系统设计：**

3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 架构设计文档
   - 核心架构
   - 工作流程
   - 数据结构
   - 通知协议
   - 异常处理

4. **[MIGRATION.md](./MIGRATION.md)** - 架构对比与迁移指南
   - 定时器轮询 vs 事件驱动
   - 性能对比
   - 迁移步骤
   - 兼容性说明

### 💻 实现指南

**开发者参考：**

5. **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - 实现指南
   - 核心模块实现
   - 代码示例
   - Agent 集成指南
   - 测试清单

## 📁 项目结构

```
proj-system/
├── INDEX.md                     # 本文档 - 文档索引
├── README.md                    # 使用指南（快速开始）
├── ARCHITECTURE.md              # 架构设计
├── IMPLEMENTATION.md            # 实现指南
├── MIGRATION.md                 # 迁移指南
├── SUBMIT_TEMPLATE.md           # 提交通知模板
│
├── workspace/                   # 项目工作区
│   └── demo-001/               # 演示项目
│       ├── project.json        # 项目元数据
│       ├── pipeline.json       # 任务编排
│       ├── deliverables/       # 交付成果
│       └── context/            # 共享上下文
│
├── orchestrator/               # 调度中心核心代码 ✅ 已实现
│   ├── index.ts               # 主入口 ✅
│   ├── notification.ts        # 通知处理 ✅
│   ├── dispatcher.ts          # 任务派发 ✅
│   ├── session-manager.ts     # Session 管理 ✅
│   └── health-monitor.ts      # 健康监控 ✅
│
└── shared/                     # 共享工具 ✅ 已实现
    ├── types.ts               # 类型定义 ✅
    ├── fs-utils.ts            # 文件工具 ✅
    └── logger.ts              # 日志工具 ✅
```

## 🎯 核心概念

### 事件驱动工作流

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Expert     │      │   调度中心    │      │    Next     │
│  Agent      │─────>│  (Orchestrator)│────>│   Agent     │
│             │      │              │      │             │
│ 1. 提交成果  │      │ 1. 接收通知   │      │ 1. 接收任务  │
│ 2. 更新进度  │      │ 2. 读取编排   │      │ 2. 执行任务  │
│ 3. 发送通知  │      │ 3. 派发下一步 │      │ 3. 循环...  │
└─────────────┘      └──────────────┘      └─────────────┘
```

### 关键文件

| 文件 | 作用 | 更新时机 |
|------|------|---------|
| `project.json` | 项目元数据和进度 | Agent 完成任务后 |
| `pipeline.json` | 任务编排流程 | 项目创建时 |
| 提交通知 | Agent → 调度中心 | 任务完成后立即 |
| 派单通知 | 调度中心 → Agent | 收到通知后立即 |

### 通知协议

**Agent → 调度中心（完成通知）：**
```markdown
【任务完成通知】

项目编号：demo-001
任务 ID：task-001
执行 Agent：product-manager

完成情况：
- 状态：✅ 已完成
- 成果路径：workspace/demo-001/deliverables/phase-1/prd.md
- 耗时：1.5 小时

请调度中心安排下一步工作。
```

**调度中心 → Agent（派单通知）：**
```markdown
【新任务派发】

项目编号：demo-001
任务 ID：task-002
任务名称：技术方案设计

上游依赖：
- task-001 ✅ 已完成

任务描述：
基于 PRD 设计技术架构

请开始执行，完成后提交通知。
```

## 🚀 快速对比

### 旧模式（定时器轮询）

```
❌ 每 5 秒轮询所有项目
❌ 响应延迟高（0-5 秒）
❌ 资源浪费（持续轮询）
❌ 扩展性差
```

### 新模式（事件驱动）

```
✅ Agent 主动通知
✅ 实时响应（<100 毫秒）
✅ 零空闲消耗
✅ 天然支持高并发
```

## 📖 阅读路径

### 角色：项目管理者

**目标：** 了解如何使用调度中心管理项目

1. [README.md](./README.md) - 快速开始
2. [SUBMIT_TEMPLATE.md](./SUBMIT_TEMPLATE.md) - 通知模板
3. [MIGRATION.md](./MIGRATION.md) - 了解架构优势

### 角色：Agent 开发者

**目标：** 为专家 Agent 集成提交通知功能

1. [SUBMIT_TEMPLATE.md](./SUBMIT_TEMPLATE.md) - 通知格式
2. [IMPLEMENTATION.md](./IMPLEMENTATION.md) - 集成指南
3. [ARCHITECTURE.md](./ARCHITECTURE.md) - 理解整体架构

### 角色：系统架构师

**目标：** 深入理解系统设计和实现

1. [ARCHITECTURE.md](./ARCHITECTURE.md) - 架构设计
2. [MIGRATION.md](./MIGRATION.md) - 架构对比
3. [IMPLEMENTATION.md](./IMPLEMENTATION.md) - 实现细节

## 🔧 工具与资源

### 演示项目

- **路径：** `workspace/demo-001/`
- **用途：** 学习事件驱动调度流程
- **包含：** 完整的 project.json + pipeline.json

### 模板文件

- **提交通知模板：** [SUBMIT_TEMPLATE.md](./SUBMIT_TEMPLATE.md)
- **派单通知模板：** [README.md](./README.md)

### 示例代码

- **通知处理器：** [IMPLEMENTATION.md](./IMPLEMENTATION.md) - 第 1 节
- **进度更新器：** [IMPLEMENTATION.md](./IMPLEMENTATION.md) - 第 2 节
- **任务派发器：** [IMPLEMENTATION.md](./IMPLEMENTATION.md) - 第 3 节

## ❓ 常见问题

### Q: 我应该从哪里开始？

**A:** 阅读 [README.md](./README.md)，5 分钟快速上手。

### Q: 如何创建新项目？

**A:** 参考 [README.md](./README.md) 的"创建新项目"章节。

### Q: Agent 如何提交通知？

**A:** 复制 [SUBMIT_TEMPLATE.md](./SUBMIT_TEMPLATE.md) 的模板，替换内容后发送。

### Q: 旧项目可以迁移到新架构吗？

**A:** 可以！参考 [MIGRATION.md](./MIGRATION.md) 的迁移步骤，只需添加提交通知逻辑。

### Q: 性能提升多少？

**A:** 响应延迟降低 25 倍，资源消耗降低 100 倍+。详见 [MIGRATION.md](./MIGRATION.md) 的性能对比。

### Q: 如何实现并行任务？

**A:** 在 `pipeline.json` 中设置相同的依赖，调度中心会自动并行派发。参考 [README.md](./README.md) 的"并行任务"章节。

## 📊 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0 | 2026-03-19 | 事件驱动架构（新） |
| v1.0 | - | 定时器轮询架构（旧） |

## 🎓 学习路线

### Level 1: 入门

- ✅ 理解事件驱动的基本概念
- ✅ 能够创建新项目
- ✅ 能够提交通知

### Level 2: 进阶

- ✅ 设计任务编排流程（pipeline.json）
- ✅ 处理并行任务
- ✅ 调试常见问题

### Level 3: 专家

- ✅ 实现调度中心核心模块
- ✅ 优化性能和可靠性
- ✅ 设计复杂的编排流程

## 📞 支持与反馈

- **文档问题：** 在对应文档目录下提 issue
- **使用问题：** 参考 [README.md](./README.md) 的常见问题
- **架构建议：** 参考 [ARCHITECTURE.md](./ARCHITECTURE.md) 的设计原则

---

**版本：** v2.0  
**更新日期：** 2026-03-19  
**维护者：** 调度中心项目组

**🎯 核心理念：** 事件驱动、实时响应、简单可靠
