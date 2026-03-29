# 执行快捷指令

**接口**: `POST /robot/shortcut/execute`  
**描述**: 执行快捷指令（如 RESET 重置）

---

## 请求

**URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot/shortcut/execute`

**Headers**:
```
access-token: <your-access-token>
Content-Type: application/json
```

**参数** (Body):

| 字段 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| command | string | 否 | 指令代码，可选值：`RESET` |
| groupId | string | 否 | 会话组 ID |
| extParams | object | 否 | 扩展参数 |

**请求示例**:
```json
{
  "command": "RESET",
  "groupId": "group_123456"
}
```

---

## 响应

**Schema**: `Result<boolean>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | boolean | 执行结果（true/false） |
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
