# 获取快捷指令列表

**接口**: `GET /robot/shortcut/list`  
**描述**: 获取会话可用快捷指令

---

## 请求

**URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot/shortcut/list`

**Headers**:
```
access-token: <your-access-token>
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| groupId | string | 否 | 会话组 ID |

---

## 响应

**Schema**: `Result<List<RobotShortcutVO>>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | array | 快捷指令列表 |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### RobotShortcutVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| code | string | 指令代码（用于执行） |
| name | string | 指令名称 |
| desc | string | 指令描述 |

**示例**:
```json
{
  "data": [
    {
      "code": "RESET",
      "name": "重置会话",
      "desc": "清空当前会话上下文"
    }
  ],
  "resultCode": 200,
  "resultMsg": "success"
}
```

---

## 脚本映射

无脚本，直接调用 API。
