# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/record/outbox

## 作用
获取当前用户的发件箱汇报列表。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageSize` | number | 是 | 每页显示个数 |
| `pageIndex` | number | 否 | 默认 1 |
| `reportRecordType` | number | 否 | 工作汇报类型：1-工作交流、2-工作指引、3-文件签批、4-AI 汇报、5-工作汇报 |
| `type` | string | 否 | 业务类型 |
| `planId` | number | 否 | 任务 ID |
| `grade` | string | 否 | 优先级：一般/紧急 |
| `empIdList` | array | 否 | 汇报人 ID 列表 |
| `beginTime` | number | 否 | 汇报时间开始（毫秒） |
| `endTime` | number | 否 | 汇报时间结束（毫秒） |
| `templateId` | number | 否 | 事项 ID |
| `templateIdList` | array | 否 | 事项 ID 列表 |
| `classificationIdList` | array | 否 | 汇报分类 ID 列表 |
| `labelId` | number | 否 | 标签 ID |
| `source` | string | 否 | 来源：detail/common |
| `orderColumn` | string | 否 | 排序字段：createTime/lastReplyTime/receiveTime |
| `readStatus` | number | 否 | 已读状态：0 未读，1 已读 |
| `laterRead` | boolean | 否 | 是否稍后阅读 |
| `mark` | boolean | 否 | 是否星标 |
| `leadEmpId` | number | 否 | 协办领导 ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "pageSize": { "type": "number" },
    "pageIndex": { "type": "number", "default": 1 },
    "reportRecordType": { "type": "number" },
    "type": { "type": "string" },
    "planId": { "type": "number" },
    "grade": { "type": "string" },
    "empIdList": { "type": "array", "items": { "type": "number" } },
    "beginTime": { "type": "number" },
    "endTime": { "type": "number" },
    "templateId": { "type": "number" },
    "templateIdList": { "type": "array", "items": { "type": "number" } },
    "classificationIdList": { "type": "array", "items": { "type": "number" } },
    "labelId": { "type": "number" },
    "source": { "type": "string" },
    "orderColumn": { "type": "string" },
    "readStatus": { "type": "number" },
    "laterRead": { "type": "boolean" },
    "mark": { "type": "boolean" },
    "leadEmpId": { "type": "number" }
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
- `../../scripts/outbox/get-list.py`
