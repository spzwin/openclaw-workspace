# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/report/readReport

## 作用
将指定汇报标记为已读，并清除当前用户下该汇报的未读提醒与新消息。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`

**Query 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reportId` | number | 是 | 汇报 ID |

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": { "type": ["null", "object", "boolean"] }
  }
}
```

## 脚本映射
- `../../scripts/report-message/read-report.py`
