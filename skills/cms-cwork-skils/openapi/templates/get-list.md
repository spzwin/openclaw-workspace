# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/template/listTemplates

## 作用
获取最近处理过的事项列表，用于发起汇报时选择事项。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beginTime` | number | 否 | 开始时间（默认一个月前，毫秒） |
| `endTime` | number | 否 | 结束时间（默认当前，毫秒） |
| `limit` | number | 否 | 限制条数 (默认 50) |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "beginTime": { "type": "number" },
    "endTime": { "type": "number" },
    "limit": { "type": "number", "default": 50 }
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
    "data": { "type": "object" }
  }
}
```

## 脚本映射
- `../../scripts/templates/get-list.py`
