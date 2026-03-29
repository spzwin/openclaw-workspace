# 删除机器人

**接口**: `POST /robot/deleteMyRobot`  
**描述**: 根据 AgentId 删除我的机器人

---

## 请求

**URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot/deleteMyRobot`

**Headers**:
```
access-token: <your-access-token>
Content-Type: application/json
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| agentId | string | 否 | 机器人 AgentID |

---

## 响应

**Schema**: `Result<boolean>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | boolean | 删除结果（true/false） |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

**示例**:
```json
{
  "data": true,
  "resultCode": 200,
  "resultMsg": "success"
}
```

---

## 脚本映射

无脚本，直接调用 API。
