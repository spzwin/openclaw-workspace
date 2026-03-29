# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/todo/completeTodo

## 作用
提交建议/决策内容并完成指定待办。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `todoId` | number | 是 | 待办 ID |
| `content` | string | 是 | 处理意见 |
| `operate` | string | 否 | 决策操作类型 (agree/disagree)，建议类待办无需传 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "todoId": { "type": "number" },
    "operate": { "type": "string" },
    "content": { "type": "string" }
  }
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": { "type": "boolean" }
  }
}
```

## 脚本映射
- `../../scripts/todos/complete.py`
