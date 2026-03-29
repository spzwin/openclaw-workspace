# 机器人模块 API 索引

**模块**: `robot`  
**基础路径**: `/robot`  
**域名**: `cwork-api-test.xgjktech.com.cn`  
**完整 URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot`

---

## 接口清单

| 接口 | 方法 | 路径 | 描述 | 文档 |
|-----|------|------|------|------|
| 注册私有机器人 | POST | `/robot/private/register` | 注册私有的 AI 机器人 | [`register-private.md`](./register-private.md) |
| 注册公开机器人 | POST | `/robot/register` | 注册 AI 机器人（公开/指定范围） | [`register.md`](./register.md) |
| 获取机器人列表 | GET | `/robot/list` | 获取当前用户可见的 AI 机器人列表 | [`list-visible.md`](./list-visible.md) |
| 删除机器人 | POST | `/robot/deleteMyRobot` | 根据 AgentId 删除我的机器人 | [`delete-my-robot.md`](./delete-my-robot.md) |
| 更新可见性 | POST | `/robot/visibility/update` | 更新机器人可见性 | [`update-visibility.md`](./update-visibility.md) |
| 获取快捷指令 | GET | `/robot/shortcut/list` | 获取会话可用快捷指令 | [`list-shortcuts.md`](./list-shortcuts.md) |
| 执行快捷指令 | POST | `/robot/shortcut/execute` | 执行快捷指令 | [`execute-shortcut.md`](./execute-shortcut.md) |

---

## 认证要求

所有接口需要在 Header 中携带：
```
access-token: <your-access-token>
Content-Type: application/json
```

详见 [`../../common/auth.md`](../../common/auth.md)

---

## 模块说明

本模块提供 AI Agent 管理 IM 机器人的完整能力：
- **注册**：支持私有注册和公开注册两种模式
- **查询**：获取机器人列表，包含在线状态、可见性等信息
- **管理**：删除机器人、更新可见性设置
- **快捷指令**：获取和执行预定义的快捷指令
