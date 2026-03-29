# POST https://notex.aishuo.co/noteX/openapi/ops/ai-chat

## 作用

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 说明 |
|---|---|---|
| `message` | string | 用户问题 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["message"],
  "properties": {
    "message": { "type": "string" }
  }
}
```

## 响应示例
```json
{
  "reply": "根据底盘数据，近期共发生了...",
  "historyCount": 3
}
```

## 超时建议

- 单次请求超时上限：`300000ms`。

## 脚本映射

- `../../scripts/creator/skills_run.py`
