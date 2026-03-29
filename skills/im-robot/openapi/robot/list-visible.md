# 获取机器人列表

**接口**: `GET /robot/list`  
**描述**: 获取当前用户可见的 AI 机器人列表

---

## 请求

**URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot/list`

**Headers**:
```
access-token: <your-access-token>
```

**参数**: 无

---

## 响应

**Schema**: `Result<List<AiRobotVO>>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | array | 机器人列表 |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### AiRobotVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 机器人 ID |
| name | string | 机器人名称 |
| agentId | string | Agent ID |
| avatar | string | 头像 URL |
| groupLabel | string | 分组标签 |
| remark | string | 备注信息 |
| userId | string | 绑定的虚拟用户 ID (employeeId) |
| extParams | object | 扩展配置 |
| isOnline | boolean | 是否在线 |
| visibleType | integer | 可见性类型：0-私有，1-公开，2-指定范围 |
| lastUseTime | integer | 最近使用时间（时间戳） |
| isDefault | boolean | 是否默认 |

**示例**:
```json
{
  "data": [
    {
      "id": "123456",
      "name": "我的私人助理",
      "agentId": "main",
      "avatar": "https://...",
      "groupLabel": "工作",
      "remark": "日常工作助手",
      "userId": "user_001",
      "extParams": {},
      "isOnline": true,
      "visibleType": 0,
      "lastUseTime": 1711180800000,
      "isDefault": true
    }
  ],
  "resultCode": 200,
  "resultMsg": "success"
}
```

---

## 脚本映射

无脚本，直接调用 API。
