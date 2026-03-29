# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/plan/searchPage

## 作用
按页获取工作任务列表。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageSize` | number | 否 | 默认 30 |
| `pageIndex` | number | 否 | 默认 1 |
| `userType` | string | 否 | 工作任务列表类型 |
| `keyWord` | string | 否 | 搜索关键词 |
| `status` | number | 否 | 状态：0-关闭，1-进行中 |
| `isRead` | number | 否 | 任务读取状态：0 未读，1 已读 |
| `reportStatus` | number | 否 | 汇报状态：0 关闭，1 待汇报，2 已汇报，3 逾期 |
| `roleType` | string | 否 | 角色类型 |
| `empIdList` | array | 否 | 人员 ID 列表 |
| `labelList` | array | 否 | 标签名称列表 |
| `grades` | array | 否 | 优先级列表 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "pageIndex": { "type": "number", "default": 1 },
    "pageSize": { "type": "number", "default": 30 },
    "userType": { "type": "string" },
    "keyWord": { "type": "string" },
    "status": { "type": "number" },
    "isRead": { "type": "number" },
    "reportStatus": { "type": "number" },
    "roleType": { "type": "string" },
    "empIdList": { "type": "array", "items": { "type": "number" } },
    "labelList": { "type": "array", "items": { "type": "string" } },
    "grades": { "type": "array", "items": { "type": "string" } }
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
- `../../scripts/tasks/get-page.py`
