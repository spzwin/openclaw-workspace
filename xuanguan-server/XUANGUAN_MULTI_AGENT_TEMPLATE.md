# Xuanguan 多 Agent 标准模板（可直接复制）

更新时间：2026-03-05
用途：快速给多个 OpenClaw Agent 复用同一套 xuanguan-server

---

## 1) 设计建议（先定策略）

推荐一机一服：
- 一个 `xuanguan-server`
- 多个 OpenClaw Agent（每个 agent 一个 accountId）

映射关系建议：
- `accountId = agent 标识`（如 `agent_default`, `agent_ops`, `agent_dev`）
- 每个 account 单独配置 `appId/appSecret` 与 allowlist

---

## 2) Server 侧模板（.env）

```env
PORT=3001
HOST=0.0.0.0
APP_ID=cli_xxxxxxxxxxxxxxxx
APP_SECRET=your_app_secret_here_change_in_production
JWT_SECRET=your_jwt_secret_change_in_production
MEDIA_BASE_URL=http://localhost:3001/media
OPENCLAW_ACCOUNT_ID=agent_default
```

> 说明：如果你用“多账户并行”，`OPENCLAW_ACCOUNT_ID` 可以保留默认路由；真正精细路由建议在插件 account 里按 agent 独立配置。

---

## 3) OpenClaw 配置模板（单 Agent）

每个 Agent 的 `~/.openclaw/openclaw.json` 可用：

```json
{
  "channels": {
    "xuanguan": {
      "enabled": true,
      "apiBaseUrl": "http://localhost:3001",
      "appId": "cli_agent_default_xxx",
      "appSecret": "secret_agent_default_xxx",
      "dmPolicy": "allowlist",
      "groupPolicy": "allowlist",
      "messageType": "text",
      "debug": true,
      "accounts": {
        "agent_default": {
          "enabled": true,
          "apiBaseUrl": "http://localhost:3001",
          "appId": "cli_agent_default_xxx",
          "appSecret": "secret_agent_default_xxx",
          "dmPolicy": "allowlist",
          "groupPolicy": "allowlist",
          "allowFrom": ["user_123456", "group_abc123"],
          "debug": true
        }
      }
    }
  },
  "plugins": {
    "enabled": true,
    "allow": ["xuanguan"],
    "entries": {
      "xuanguan": { "enabled": true }
    }
  }
}
```

生效：
```bash
openclaw gateway restart
```

---

## 4) 多 Agent 账户模板（同一个 Agent 实例中）

如果你确实要在“同一个 OpenClaw 实例”里挂多个 xuanguan 账户：

```json
"channels": {
  "xuanguan": {
    "enabled": true,
    "accounts": {
      "agent_default": {
        "enabled": true,
        "apiBaseUrl": "http://localhost:3001",
        "appId": "cli_agent_default_xxx",
        "appSecret": "secret_default",
        "dmPolicy": "allowlist",
        "groupPolicy": "allowlist",
        "allowFrom": ["user_a", "group_x"]
      },
      "agent_ops": {
        "enabled": true,
        "apiBaseUrl": "http://localhost:3001",
        "appId": "cli_agent_ops_xxx",
        "appSecret": "secret_ops",
        "dmPolicy": "allowlist",
        "groupPolicy": "allowlist",
        "allowFrom": ["user_b", "group_y"]
      }
    }
  }
}
```

---

## 5) 迁移到新 Agent 的标准步骤

1. 复制 xuanguan 插件目录到新机器（或确保存在）
2. 新 Agent 写入 `openclaw.json` 的 xuanguan 配置
3. 确认 `apiBaseUrl/appId/appSecret` 正确
4. `openclaw gateway restart`
5. 用 `chat.html` 发一条 inbound 验收

---

## 6) 验收命令模板

```bash
# 1) server 在线
curl http://localhost:3001/health
curl http://localhost:3001/stats

# 2) channel 配置识别
openclaw channels status --json --probe

# 3) 核心指标（应看到 xuanguan configured=true）
# - channels.xuanguan.configured=true
# - channelAccounts.xuanguan[].configured=true
```

业务验收：
- 页面发消息 -> `deliveredToAgent=true`
- Agent 回复 -> 页面可见

---

## 7) 生产建议（强烈）

- 不要使用 `dmPolicy=open` + `allowFrom=["*"]`
- 生产统一改：
  - `dmPolicy=allowlist`
  - `groupPolicy=allowlist`
  - `allowFrom` 仅保留明确 user/group
- `debug=false`，避免日志泄露
- 定期轮换 `appSecret`

---

## 8) 快速排错模板

### 现象：页面发了，Agent 无反应
- 看 `inbound/send` 是否 `deliveredToAgent=true`
- 看 `openclaw channels status` 里 xuanguan 是否 loaded/configured

### 现象：Agent 回复了，页面没收到
- 看插件日志有无 `send.message 404`
- 重点检查 `conversationId` 是否传原值（`group_xxx/single_xxx`）

### 现象：插件突然没了
- 大概率插件加载失败（语法/类型错误）
- 执行 `openclaw gateway restart` 后看日志首条报错

---

## 9) 建议命名规范

- accountId：`agent_<name>`，如 `agent_default/agent_ops/agent_dev`
- 会话 id：
  - 群：`group_<uuid>`
  - 私聊：`single_<uuid>`
- 这样跨 Agent 日志检索最清晰
