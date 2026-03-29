# 注册公开机器人

**接口**: `POST /robot/register`  
**描述**: 注册 AI 机器人（支持私有、公开、指定范围可见）

---

## 请求

**URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot/register`

**Headers**:
```
access-token: <your-access-token>
Content-Type: application/json
```

**参数** (Body):

| 字段 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| name | string | ✓ | 机器人名称 |
| agentId | string | 否 | 绑定的外部 Agent ID，例如：main |
| avatar | string | 否 | 机器人头像 URL |
| groupLabel | string | 否 | 分组标签 |
| remark | string | 否 | 备注信息 |
| visibleType | integer | 否 | 可见性类型：0-私有 (默认)，1-公开，2-指定范围 |
| visibleRange | array | 否 | 可见范围列表（visibleType=2 时必传） |

### visibleRange 项结构

| 字段 | 类型 | 描述 |
|-----|------|------|
| targetId | string | 目标 ID |
| targetType | string | 目标类型：USER-人员，DEPT-部门 |

**请求示例**（公开机器人）:
```json
{
  "name": "公共助手",
  "agentId": "public-bot",
  "avatar": "https://example.com/avatar.png",
  "visibleType": 1
}
```

**请求示例**（指定范围可见）:
```json
{
  "name": "团队助手",
  "agentId": "team-bot",
  "visibleType": 2,
  "visibleRange": [
    {"targetId": "user_001", "targetType": "USER"},
    {"targetId": "dept_002", "targetType": "DEPT"}
  ]
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
    "agentId": "public-bot",
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
