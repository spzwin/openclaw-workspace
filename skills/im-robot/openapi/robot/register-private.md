# 注册私有机器人

**接口**: `POST /robot/private/register`  
**描述**: 注册私有的 AI 机器人（仅自己可见）

---

## 请求

**URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot/private/register`

**Headers**:
```
access-token: <your-access-token>
Content-Type: application/json
```

**参数** (Body):

| 字段 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| agentId | string | ✓ | 绑定的外部 Agent ID，例如：main |
| name | string | 否 | 机器人名称，为空默认取用户姓名+'的私人助理' |
| avatar | string | 否 | 机器人头像 URL，为空取默认机器人头像 |
| groupLabel | string | 否 | 分组标签 |
| remark | string | 否 | 备注信息 |

**请求示例**:
```json
{
  "agentId": "main",
  "name": "我的私人助理",
  "avatar": "https://example.com/avatar.png",
  "groupLabel": "工作",
  "remark": "日常工作助手"
}
```

---

## 响应

**Schema**: `Result<RobotPluginVO>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | RobotPluginVO | 机器人详情 |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### RobotPluginVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| agentId | string | Agent ID |
| appKey | string | 机器人的认证 AppKey |
| userId | string | 绑定的虚拟用户 ID (employeeId) |
| baseUrl | string | 后台服务域名 |
| wsBaseUrl | string | 后台服务 wss 域名 |

**响应示例**:
```json
{
  "data": {
    "agentId": "main",
    "appKey": "ak_xxxxxxxxxxxx",
    "userId": "user_001",
    "baseUrl": "https://cwork-api-test.xgjktech.com.cn",
    "wsBaseUrl": "wss://cwork-api-test.xgjktech.com.cn"
  },
  "resultCode": 200,
  "resultMsg": "success"
}
```

---

## 脚本映射

无脚本，直接调用 API。
