# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/template/listByIds

## 作用
按事项 ID 列表批量获取事项简易信息。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
请求体为 JSON 数组。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `templateIds` | array | 是 | 事项 ID 列表；请求体直接传数组 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "number"
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
    "data": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "templateId": { "type": "number" },
          "main": { "type": "string" }
        }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/templates/get-by-ids.py`
