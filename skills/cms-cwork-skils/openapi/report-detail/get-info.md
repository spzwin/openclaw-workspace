# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/info

## 作用
获取指定汇报的完整结构化详情，包含汇报人、时间、各层级内容及结果。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reportId` | string | 是 | 汇报 ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {}
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
- `../../scripts/report-detail/get-info.py`
