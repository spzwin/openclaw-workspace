# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/reportInfoOpenQuery/isReportRead

## 作用
根据汇报 ID 和员工 ID 判断该员工是否已读指定汇报。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`

**Query 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reportId` | number | 是 | 汇报 ID |
| `employeeId` | number | 是 | 员工 ID |

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
- `../../scripts/report-query/is-report-read.py`
