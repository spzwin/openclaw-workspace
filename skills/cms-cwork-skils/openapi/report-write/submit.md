# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/record/submit

## 作用
创建并提交一条汇报记录，支持关联任务/事项、接收人/抄送人、多级节点及附件。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `planId` | number | 否 | 工作任务 ID |
| `templateId` | number | 否 | 事项 ID |
| `typeId` | number | 否 | 业务类型 ID，默认 9999 |
| `main` | string | 是 | 汇报标题 |
| `grade` | string | 否 | 优先级：一般/紧急 |
| `privacyLevel` | string | 否 | 密级：非涉密/涉密 |
| `contentType` | string | 否 | 正文类型：html/markdown |
| `contentHtml` | string | 是 | 汇报内容 |
| `acceptEmpIdList` | array | 否 | 接收人 ID 列表；仅在 `reportLevelList` 为空时兜底 |
| `copyEmpIdList` | array | 否 | 抄送人 ID 列表 |
| `reportLevelList` | array | 否 | 多级节点用户列表；接收人以该字段为准 |
| `fileVOList` | array | 否 | 附件列表 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "planId": { "type": "number" },
    "templateId": { "type": "number" },
    "typeId": { "type": "number", "default": 9999 },
    "main": { "type": "string" },
    "grade": { "type": "string" },
    "privacyLevel": { "type": "string" },
    "contentType": { "type": "string", "default": "html" },
    "contentHtml": { "type": "string" },
    "acceptEmpIdList": { "type": "array", "items": { "type": "number" } },
    "copyEmpIdList": { "type": "array", "items": { "type": "number" } },
    "reportLevelList": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string" },
          "level": { "type": "number" },
          "nodeCode": { "type": "string" },
          "nodeName": { "type": "string" },
          "levelUserList": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "empId": { "type": "number" },
                "requirement": { "type": "string" }
              }
            }
          }
        }
      }
    },
    "fileVOList": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "fileId": { "type": "string" },
          "name": { "type": "string" },
          "type": { "type": "string" },
          "fsize": { "type": "number" },
          "url": { "type": "string" }
        }
      }
    }
  },
  "required": ["main", "contentHtml"]
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
    "data": {
      "type": "object",
      "properties": {
        "id": { "type": "number" }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/report-write/submit.py`
