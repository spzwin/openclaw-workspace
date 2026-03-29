# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/report/aiSseQaV2

## 作用
针对指定汇报集合进行 AI SSE 问答。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`
- `Accept: text/event-stream`

**响应类型**
- `text/event-stream`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `userContent` | string | 是 | 问答内容 |
| `aiType` | number | 否 | 默认固定 42 |
| `reportIdList` | array | 是 | 需要关联对话的汇报 ID 列表 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "userContent": { "type": "string" },
    "aiType": { "type": "number", "default": 42 },
    "reportIdList": { "type": "array", "items": { "type": "number" } }
  },
  "required": ["userContent", "reportIdList"]
}
```

## 响应说明
原始 OpenAPI 直接返回 SSE 事件流；当前脚本会将事件流聚合后再输出为 JSON。

## 脚本映射
- `../../scripts/ai-qa/ask-sse.py`
