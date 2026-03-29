# im-robot — IM AI 机器人管理

**版本**: v1.0  
**描述**: 为 AI Agent 提供 IM 机器人管理能力（注册、查询、删除、可见性控制、快捷指令）

---

## 能力概览

本 Skill 提供 AI Agent 管理 IM 机器人所需的完整能力：

| 能力模块 | 功能 | 接口数 |
|---------|------|--------|
| 机器人注册 | 注册私有/公开机器人 | 2 |
| 机器人管理 | 查询列表、删除、更新可见性 | 3 |
| 快捷指令 | 获取指令列表、执行指令 | 2 |

---

## 模块路由

当用户意图匹配以下场景时，加载对应模块：

| 用户意图 | 路由模块 | 触发示例 |
|---------|---------|---------|
| "注册一个机器人" | `robot/register` | "帮我注册一个私人助理机器人" |
| "查看机器人列表" | `robot/list` | "我有哪些机器人？" |
| "删除机器人" | `robot/delete` | "删除 agentId 为 main 的机器人" |
| "设置可见性" | `robot/visibility` | "把这个机器人设为公开" |
| "执行快捷指令" | `robot/shortcut` | "执行 RESET 指令" |

---

## 宪章

**AI Agent 优先**：所有接口设计和描述都以 AI Agent 为使用对象，语言简洁、参数明确。

**最小必需字段**：只保留 AI Agent 实际需要的字段，避免信息过载。

**生产就绪**：文档中的域名、认证方式均为生产环境配置。

---

## 工作流

```
用户请求 → 意图识别 → 加载模块 → 调用接口 → 返回结果
```

1. **意图识别**：根据用户自然语言判断操作类型
2. **模块加载**：加载对应模块的 `api-index.md` 和接口文档
3. **接口调用**：按文档规范构造请求
4. **结果处理**：解析响应，返回给用户

---

## 加载规则

- **默认不加载**：本 Skill 不会在会话启动时自动加载
- **按需加载**：当用户请求匹配模块路由时，动态加载对应模块
- **认证前置**：首次调用前必须先完成认证（见 `common/auth.md`）

---

## 能力树

```
im-robot/
├── SKILL.md                              # 本文件
├── common/
│   ├── auth.md                           # 认证规范
│   └── conventions.md                    # 通用约束
├── openapi/
│   ├── common/
│   │   └── appkey.md                     # Token 交换接口
│   └── robot/
│       ├── api-index.md                  # 机器人模块接口索引
│       ├── delete-my-robot.md            # 删除机器人
│       ├── list-visible.md               # 获取机器人列表
│       ├── register-private.md           # 注册私有机器人
│       ├── register.md                   # 注册公开机器人
│       ├── execute-shortcut.md           # 执行快捷指令
│       ├── list-shortcuts.md             # 获取快捷指令列表
│       └── update-visibility.md          # 更新机器人可见性
├── examples/
│   └── robot/
│       └── README.md                     # 使用示例
└── scripts/
    └── robot/
        └── README.md                     # 脚本清单（无脚本）
```

---

## 依赖

- **认证**：`access-token`（见 `common/auth.md`）
- **网络**：需要能访问 API 域名 `cwork-api-test.xgjktech.com.cn`
