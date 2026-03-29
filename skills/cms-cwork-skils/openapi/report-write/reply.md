# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/record/reply

## 作用
对指定汇报进行回复，可带附件、@人和通知控制。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reportRecordId` | string | 是 | 工作汇报 ID |
| `isMedia` | number | 否 | 是否带附件：0/1 |
| `mediaVOList` | array | 否 | 附件列表 |
| `contentHtml` | string | 是 | 回复内容 |
| `sendMsg` | boolean | 否 | 是否通知汇报人，默认 true |
| `addEmpIdList` | array | 否 | 被 @ 的员工 ID 集合 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "reportRecordId": { "type": "string" },
    "isMedia": { "type": "number", "default": 0 },
    "mediaVOList": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "fileId": { "type": "string" },
          "fsize": { "type": "number" },
          "name": { "type": "string" },
          "type": { "type": "string" }
        }
      }
    },
    "contentHtml": { "type": "string" },
    "sendMsg": { "type": "boolean", "default": true },
    "addEmpIdList": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["reportRecordId", "contentHtml"]
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "resultMsg": { "type": ["string", "null"] },
    "data": { "type": "number" }
  }
}
```

## 脚本映射
- `../../scripts/report-write/reply.py`
