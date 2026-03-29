# 玄关消息系统 - 快速启动指南

> 5 分钟快速测试玄关消息系统

---

## 🚀 快速开始（5 分钟）

### 第 1 步：启动服务端

```bash
# 进入目录
cd ~/.openclaw/workspace/xuanguan-server

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 修改密钥（至少修改 APP_SECRET 和 JWT_SECRET）

# 启动服务（开发模式）
npm run dev
```

**看到以下输出表示成功**：
```
============================================================
🚀 玄关消息系统服务端已启动
============================================================
📡 HTTP: http://0.0.0.0:3000
🔌 WebSocket: ws://0.0.0.0:3000/ws/messages
📊 健康检查：http://0.0.0.0:3000/health
📈 连接统计：http://0.0.0.0:3000/stats
============================================================
```

---

### 第 2 步：打开 Web Chat 测试页面

在浏览器中打开：

```
http://localhost:3000/chat.html
```

**Web Chat 功能**：
- ✅ 配置 API 地址和应用信息
- ✅ 一键连接 WebSocket
- ✅ 发送文本消息
- ✅ 接收推送消息
- ✅ 实时日志查看
- ✅ 连接状态显示

---

### 第 3 步：测试消息

#### 方法 1：使用 Web Chat

1. 打开 `http://localhost:3000/chat.html`
2. 默认配置已填好（如果没改过 .env）
3. 点击"连接"按钮
4. 在输入框输入消息，按回车发送
5. 查看日志面板（点击"显示/隐藏日志"）

#### 方法 2：使用测试脚本

```bash
cd ~/.openclaw/workspace/xuanguan-server
./test.sh
```

#### 方法 3：使用 curl 命令

```bash
# 1. 获取 Token
curl -X POST http://localhost:3000/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "appId": "cli_xxxxxxxxxxxxxxxx",
    "appSecret": "your_app_secret_here",
    "grantType": "client_credentials"
  }'

# 2. 发送消息
TOKEN="上一步返回的 accessToken"
curl -X POST http://localhost:3000/api/v1/message/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "user_123456",
    "conversationType": "single",
    "msgType": "text",
    "content": {"text": "你好"}
  }'
```

---

## 📝 配置说明

### .env 文件配置

```env
# 必要配置（必须修改）
APP_SECRET=修改为你的密钥              # 至少 16 字符
JWT_SECRET=修改为你的 JWT 密钥          # 至少 32 字符

# 可选配置
PORT=3000                               # HTTP 端口
APP_ID=cli_xxxxxxxxxxxxxxxx             # 应用 ID
JWT_EXPIRES_IN=2h                       # Token 有效期
MEDIA_STORAGE_PATH=/tmp/xuanguan/media  # 媒体存储路径
```

### Web Chat 配置

| 字段 | 说明 | 默认值 |
|------|------|--------|
| API 地址 | 服务端地址 | `http://localhost:3000` |
| App ID | 应用 ID | `cli_xxxxxxxxxxxxxxxx` |
| App Secret | 应用密钥 | `.env` 中的 `APP_SECRET` |
| 用户 ID | 接收消息的用户 | `user_123456` |

---

## 🧪 测试清单

### 基础功能测试

- [ ] 访问 `http://localhost:3000/health` 返回 OK
- [ ] Web Chat 可以连接成功
- [ ] 可以发送文本消息
- [ ] 可以接收推送消息
- [ ] 日志显示正常

### 进阶功能测试

- [ ] 发送图片消息
- [ ] 批量发送消息
- [ ] 消息撤回
- [ ] 已读回执
- [ ] 媒体上传

---

## 🔧 常见问题

### 1. 连接失败

**错误**: `ECONNREFUSED`

**解决**:
```bash
# 检查服务是否启动
curl http://localhost:3000/health

# 检查端口是否被占用
lsof -i :3000

# 重启服务
npm run dev
```

### 2. Token 获取失败

**错误**: `Invalid appId or appSecret`

**解决**:
```bash
# 检查 .env 配置
cat .env | grep APP_SECRET

# 确保 appId 和 appSecret 匹配
# 默认：appId=cli_xxxxxxxxxxxxxxxx
#      appSecret=your_app_secret_here
```

### 3. WebSocket 连接失败

**错误**: `WebSocket connection failed`

**解决**:
```bash
# 检查 WebSocket 端点
wscat -c "ws://localhost:3000/ws/messages?appId=cli_xxxxxxxxxxxxxxxx"

# 查看服务端日志
# 开发模式会自动输出日志
```

### 4. 消息发送失败

**错误**: `Invalid or expired token`

**解决**:
```bash
# 重新获取 Token
# Web Chat 中点击"断开"，然后重新"连接"
```

---

## 📊 监控和调试

### 查看健康状态

```bash
curl http://localhost:3000/health | jq .
```

### 查看连接统计

```bash
curl http://localhost:3000/stats | jq .
```

### 查看日志

开发模式下，日志会直接输出到终端。

生产模式：
```bash
tail -f /tmp/xuanguan/server.log
```

### 调试 WebSocket

```bash
# 安装 wscat
npm install -g wscat

# 连接 WebSocket
wscat -c "ws://localhost:3000/ws/messages?appId=cli_xxxxxxxxxxxxxxxx&accountId=user_123456"

# 发送心跳
{"type": "heartbeat", "timestamp": 1709550000000}
```

---

## 🎯 下一步

### 集成 OpenClaw

```bash
# 1. 安装插件
cd ~/.openclaw/workspace/xuanguan
openclaw plugins install -l .

# 2. 配置渠道
openclaw configure --section channels
# 选择 xuanguan，填写 API 信息

# 3. 重启 Gateway
openclaw gateway restart
```

### 生产部署

1. 修改 `.env` 中的默认密钥
2. 配置 HTTPS（Nginx 反向代理）
3. 设置数据库持久化
4. 配置监控和告警
5. 设置防火墙规则

---

## 📚 相关文档

- [API 规范](../xuanguan/API_SPEC.md)
- [插件实现](../xuanguan/)
- [完整文档](README.md)

---

## 🆘 获取帮助

遇到问题？

1. 查看日志输出
2. 检查 `.env` 配置
3. 运行 `./test.sh` 测试
4. 查看 [CHECKLIST.md](../xuanguan/CHECKLIST.md)

---

**祝测试顺利！** 🎉
