# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/plan/getSimplePlanAndReportInfo

## 作用
获取单个任务的简易信息，以及该任务关联的汇报简易信息列表。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`

**Query 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `planId` | number | 是 | 工作任务 ID |

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": {
      "type": "object",
      "properties": {
        "id": { "type": "number" },
        "main": { "type": "string" },
        "status": { "type": "number" },
        "reportList": { "type": "array" }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/tasks/get-simple-plan-and-report-info.py`
