# Xuanguan 全链路对接与迁移文档（可复用到其它 Agent）

更新时间：2026-03-05（Asia/Shanghai）
状态：✅ 已打通（页面 ↔ xuanguan-server ↔ OpenClaw xuanguan 插件 ↔ Agent）

---

## 1. 架构总览

```text
Web Chat (chat.html)
   ↓ (HTTP + WS)
xuanguan-server (3001)
   ↓ (WS inbound push)
OpenClaw xuanguan channel plugin
   ↓ (dispatch)
Agent Session
   ↓ (send)
OpenClaw xuanguan channel plugin
   ↓ (HTTP /api/v1/message/send)
xuanguan-server
   ↓ (WS push)
Web Chat
```

关键闭环：
- 入站：页面发消息 → `/api/v1/message/inbound/send` → 插件收到 → Agent
- 出站：Agent 回复 → 插件 `/api/v1/message/send` → 页面收到

---

## 2. 工程配置（xuanguan-server）

## 2.1 .env 示例

```env
PORT=3001
HOST=0.0.0.0
APP_ID=cli_xxxxxxxxxxxxxxxx
APP_SECRET=your_app_secret_here_change_in_production
JWT_SECRET=your_jwt_secret_change_in_production
MEDIA_BASE_URL=http://localhost:3001/media
OPENCLAW_ACCOUNT_ID=default
```

说明：
- `APP_ID/APP_SECRET`：与 OpenClaw 插件配置保持一致
- `OPENCLAW_ACCOUNT_ID`：server 将 inbound 消息推送到该 account（默认 `default`）

## 2.2 启动命令

```bash
cd ~/.openclaw/workspace/xuanguan-server
npm install
npm run dev
```

健康检查：
```bash
curl http://localhost:3001/health
curl http://localhost:3001/stats
```

页面地址：
```text
http://localhost:3001/chat.html
```

---

## 3. OpenClaw 插件配置（关键）

文件：`~/.openclaw/openclaw.json`

```json
{
  "channels": {
    "xuanguan": {
      "enabled": true,
      "apiBaseUrl": "http://localhost:3001",
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "your_app_secret_here_change_in_production",
      "dmPolicy": "open",
      "groupPolicy": "open",
      "messageType": "text",
      "debug": true,
      "accounts": {
        "default": {
          "enabled": true,
          "apiBaseUrl": "http://localhost:3001",
          "appId": "cli_xxxxxxxxxxxxxxxx",
          "appSecret": "your_app_secret_here_change_in_production",
          "dmPolicy": "open",
          "groupPolicy": "open",
          "allowFrom": ["*"],
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

修改后生效：
```bash
openclaw gateway restart
```

状态检查：
```bash
openclaw channels status --json --probe
```

期望：
- `channels.xuanguan.configured = true`
- `channelAccounts.xuanguan[0].configured = true`

---

## 4. 对接接口约定（server）

## 4.1 页面/客户端
- `POST /oauth/token`
- `GET /api/v1/message/conversations?userId=...`
- `POST /api/v1/message/conversations`
- `GET /api/v1/message/conversations/:conversationId/messages`
- `POST /api/v1/message/inbound/send`（用户 → Agent）

## 4.2 插件/Agent 出站
- `POST /api/v1/message/send`（Agent → 用户）

注意：
- `conversationId` 必须传完整值（如 `group_xxx` / `single_xxx`），**不要去掉前缀**。

---

## 5. 迁移到其它 Agent 的步骤

1) 复制 server
- 将 `xuanguan-server` 部署到目标机器（或同机）
- 配置 `.env`（端口、APP_ID/SECRET）

2) 复制插件
- 确保 `~/.openclaw/extensions/xuanguan` 存在（同版本）

3) 配置 OpenClaw
- 在目标 Agent 的 `openclaw.json` 添加 `channels.xuanguan`
- `apiBaseUrl/appId/appSecret` 指向新 server
- 账户名可继续用 `default`，或按 agent 自定义（如 `ops`, `sales`）

4) 重启网关
```bash
openclaw gateway restart
```

5) 验收
- `openclaw channels status --probe` 看 xuanguan 已 configured
- 打开 `chat.html` 发 inbound，看主会话出现 `xuanguan:g-...` session
- 让 Agent 回复，确认页面可收到

---

## 6. 多 Agent 推荐配置

可共用同一个 xuanguan-server，通过 account 区分：

```json
"accounts": {
  "default": { ... },
  "agent_ops": {
    "enabled": true,
    "apiBaseUrl": "http://localhost:3001",
    "appId": "cli_ops_xxx",
    "appSecret": "ops_secret",
    "dmPolicy": "allowlist",
    "groupPolicy": "allowlist",
    "allowFrom": ["user_1", "group_xxx"]
  }
}
```

建议：
- 测试环境：`open + allowFrom ["*"]`
- 生产环境：`allowlist` + 精确 user/group 白名单

---

## 7. 常见故障排查

1) 页面发了但 Agent 无反应
- 看 `/stats` 是否有 `default` 连接
- 看 `inbound/send` 返回是否 `deliveredToAgent=true`
- 看 `openclaw channels status` 中 xuanguan 是否存在

2) Agent 回复了但页面收不到
- 检查插件日志是否有 `send.message ... 404`
- 通常是 `conversationId` 被错误转换（前缀丢失）

3) 插件加载失败
- 看 `openclaw` 日志是否 ParseError/TypeError
- 修复后执行一次 `openclaw gateway restart`

---

## 8. 当前关键文件清单

### Server
- `src/message.ts`（路由与消息中转）
- `src/store.ts`（会话/消息内存存储）
- `public/chat.html`（Web 聊天页）

### Plugin
- `~/.openclaw/extensions/xuanguan/index.ts`
- `~/.openclaw/extensions/xuanguan/src/channel.ts`
- `~/.openclaw/extensions/xuanguan/src/connection-manager.ts`
- `~/.openclaw/extensions/xuanguan/src/send-service.ts`

---

## 9. 迁移最小检查清单（可复制）

- [ ] xuanguan-server `/health` OK
- [ ] chat 页面可访问
- [ ] `channels.xuanguan.configured=true`
- [ ] inbound 返回 `deliveredToAgent=true`
- [ ] Agent 回复能回到页面
- [ ] 生产环境已收敛 `allowFrom` 与 policy

---

如需，我可以再给你补一份 `XUANGUAN_PROD_HARDENING.md`（生产安全配置模板：鉴权、白名单、日志与告警）。
