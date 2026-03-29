#!/bin/bash

# 玄关消息系统 - 快速测试脚本

BASE_URL="http://localhost:3001"
APP_ID="cli_xxxxxxxxxxxxxxxx"
APP_SECRET="your_app_secret_here_change_in_production"

echo "======================================"
echo "  玄关消息系统 - 快速测试"
echo "======================================"
echo ""

# 1. 健康检查
echo "1️⃣  健康检查..."
curl -s "$BASE_URL/health" | jq .
echo ""

# 2. 获取 Token
echo "2️⃣  获取 Token..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/oauth/token" \
  -H "Content-Type: application/json" \
  -d "{
    \"appId\": \"$APP_ID\",
    \"appSecret\": \"$APP_SECRET\",
    \"grantType\": \"client_credentials\"
  }")

echo "$TOKEN_RESPONSE" | jq .

TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.data.accessToken')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ 获取 Token 失败！"
  exit 1
fi

echo "✅ Token: $TOKEN"
echo ""

# 3. 发送文本消息
echo "3️⃣  发送文本消息..."
curl -s -X POST "$BASE_URL/api/v1/message/send" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "user_123456",
    "conversationType": "single",
    "msgType": "text",
    "content": {
      "text": "你好，我是 AI 助手！"
    }
  }' | jq .
echo ""

# 4. 发送 Markdown 消息
echo "4️⃣  发送 Markdown 消息..."
curl -s -X POST "$BASE_URL/api/v1/message/send" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "user_123456",
    "conversationType": "single",
    "msgType": "markdown",
    "content": {
      "text": "## 欢迎\n\n这是一条 **Markdown** 消息\n\n- 列表项 1\n- 列表项 2"
    }
  }' | jq .
echo ""

# 5. 批量发送消息
echo "5️⃣  批量发送消息..."
curl -s -X POST "$BASE_URL/api/v1/message/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "conversationId": "user_123",
        "conversationType": "single",
        "msgType": "text",
        "content": {"text": "消息 1"}
      },
      {
        "conversationId": "user_456",
        "conversationType": "single",
        "msgType": "text",
        "content": {"text": "消息 2"}
      }
    ]
  }' | jq .
echo ""

# 6. 查看连接统计
echo "6️⃣  查看连接统计..."
curl -s "$BASE_URL/stats" | jq .
echo ""

# 7. WebSocket 测试提示
echo "======================================"
echo "7️⃣  WebSocket 测试"
echo "======================================"
echo ""
echo "使用以下命令测试 WebSocket:"
echo ""
echo "  wscat -c \"ws://localhost:3000/ws/messages?appId=$APP_ID&accountId=user_123456\""
echo ""
echo "连接后发送心跳:"
echo '  {"type": "heartbeat", "timestamp": '$(date +%s)'000}'
echo ""
echo "======================================"
echo "✅ 测试完成！"
echo "======================================"
