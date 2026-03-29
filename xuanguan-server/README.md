# 玄关消息系统 - 服务端实现

> OpenClaw Channel 插件配套服务端  
> 版本：v1.0.0  
> 日期：2026-03-04

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/xuanguan-server
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，修改密钥
```

**必要配置**:
```env
APP_SECRET=修改为你的密钥
JWT_SECRET=修改为你的 JWT 密钥
```

### 3. 启动服务

**开发模式** (自动重载):
```bash
npm run dev
```

**生产模式**:
```bash
npm run build
npm start
```

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:3000/health

# 获取 Token
curl -X POST http://localhost:3000/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "appId": "cli_xxxxxxxxxxxxxxxx",
    "appSecret": "your_app_secret_here",
    "grantType": "client_credentials"
  }'

# WebSocket 测试
wscat -c "ws://localhost:3000/ws/messages?appId=cli_xxxxxxxxxxxxxxxx"
```

---

## 📁 项目结构

```
xuanguan-server/
├── src/
│   ├── index.ts           # 主入口
│   ├── types.ts           # 类型定义
│   ├── auth.ts            # 认证模块
│   ├── websocket.ts       # WebSocket 服务
│   ├── message.ts         # 消息路由
│   └── media.ts           # 媒体路由
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

---

## 🔌 API 接口

### 认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/oauth/token` | POST | 获取访问令牌 |

### 消息

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/message/send` | POST | 发送消息 |
| `/api/v1/message/batch` | POST | 批量发送 |
| `/api/v1/message/recall` | POST | 撤回消息 |
| `/api/v1/message/ack` | POST | 已读回执 |
| `/api/v1/message/:id` | GET | 获取消息详情 |

### 媒体

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/media/upload` | POST | 上传媒体 |
| `/api/v1/media/:id` | GET | 下载媒体 |
| `/media/:filename` | GET | 静态文件访问 |

### WebSocket

| 端点 | 说明 |
|------|------|
| `/ws/messages` | WebSocket 消息推送 |

---

## 🧪 测试示例

### 发送文本消息

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:3000/api/v1/message/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "user_123456",
    "conversationType": "single",
    "msgType": "text",
    "content": {
      "text": "你好，我是 AI 助手"
    }
  }'
```

### 上传图片

```bash
curl -X POST http://localhost:3000/api/v1/media/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "type=image"
```

### WebSocket 接收消息

```bash
# 安装 wscat
npm install -g wscat

# 连接
wscat -c "ws://localhost:3000/ws/messages?appId=cli_xxxxxxxxxxxxxxxx&accountId=user_123456"

# 发送心跳
{"type": "heartbeat", "timestamp": 1709550000000}
```

---

## ⚙️ 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 3000 | HTTP 服务端口 |
| `HOST` | 0.0.0.0 | 监听地址 |
| `APP_ID` | cli_xxx | 应用 ID |
| `APP_SECRET` | - | 应用密钥 |
| `JWT_SECRET` | - | JWT 密钥 |
| `JWT_EXPIRES_IN` | 2h | Token 有效期 |
| `MEDIA_STORAGE_PATH` | /tmp/xuanguan/media | 媒体存储路径 |
| `MEDIA_BASE_URL` | http://localhost:3000 | 媒体访问 URL |
| `LOG_LEVEL` | info | 日志级别 |
| `RATE_LIMIT_PER_MINUTE` | 300 | 每分钟限流 |
| `WS_HEARTBEAT_INTERVAL` | 30000 | WebSocket 心跳间隔 |

---

## 🛡️ 安全建议

### 生产环境配置

1. **修改默认密钥**:
```env
APP_SECRET=使用强随机字符串
JWT_SECRET=使用强随机字符串（至少 32 字符）
```

2. **启用 HTTPS**:
```bash
# 使用 Nginx 反向代理
# 或使用 Let's Encrypt 证书
```

3. **配置防火墙**:
```bash
# 只开放必要端口
ufw allow 3000/tcp
ufw allow 443/tcp
```

4. **限流保护**:
```env
RATE_LIMIT_PER_MINUTE=100
```

---

## 📊 监控

### 健康检查

```bash
curl http://localhost:3000/health
```

响应:
```json
{
  "status": "ok",
  "timestamp": 1709550000000,
  "uptime": 3600,
  "memory": {
    "rss": 102400000,
    "heapUsed": 51200000
  }
}
```

### 连接统计

```bash
curl http://localhost:3000/stats
```

响应:
```json
{
  "status": "ok",
  "websocket": {
    "totalAccounts": 10,
    "totalConnections": 15,
    "byAccount": {
      "user_123": 1,
      "user_456": 2
    }
  }
}
```

---

## 🐛 调试

### 查看日志

```bash
# 开发模式会自动输出日志
# 生产模式查看日志文件
tail -f /tmp/xuanguan/server.log
```

### 调试 WebSocket

```bash
# 使用 wscat  verbose 模式
wscat -c "ws://localhost:3000/ws/messages?appId=xxx" -v
```

### 测试工具

- **Postman**: API 测试
- **wscat**: WebSocket 测试
- **curl**: 命令行测试

---

## 📝 待实现功能

- [ ] 数据库持久化（目前使用内存存储）
- [ ] 用户/群组管理
- [ ] 消息已读回执推送
- [ ] 分片上传（大文件）
- [ ] 媒体转换（压缩、格式转换）
- [ ] 消息搜索
- [ ] 群组管理 API

---

## 🔗 相关文档

- [API 规范](../API_SPEC.md)
- [插件实现](../xuanguan/)
- [增强功能](../ENHANCEMENTS.md)

---

## 📄 许可

MIT License
