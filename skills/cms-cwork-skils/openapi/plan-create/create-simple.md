# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/report/plan/create

## 作用
创建一个高级工作任务，并分配汇报人及其他干系人。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `main` | string | 是 | 任务名称 |
| `needful` | string | 是 | 任务描述/要求 |
| `typeId` | number | 是 | 业务类型 ID |
| `reportEmpIdList` | array | 是 | 汇报人员 ID 列表 |
| `target` | string | 是 | 任务目标 |
| `ownerEmpIdList` | array | 否 | 责任人 ID 列表 |
| `assistEmpIdList` | array | 否 | 协办人 ID 列表 |
| `supervisorEmpIdList` | array | 否 | 监督人 ID 列表 |
| `copyEmpIdList` | array | 否 | 抄送人 ID 列表 |
| `observerEmpIdList` | array | 否 | 观察者 ID 列表 |
| `endTime` | number | 是 | 任务结束时间戳（毫秒） |
| `pushNow` | number | 否 | 创建后是否立即推送：0/1 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "main": { "type": "string" },
    "needful": { "type": "string" },
    "typeId": { "type": "number" },
    "reportEmpIdList": { "type": "array", "items": { "type": "number" } },
    "target": { "type": "string" },
    "ownerEmpIdList": { "type": "array", "items": { "type": "number" } },
    "assistEmpIdList": { "type": "array", "items": { "type": "number" } },
    "supervisorEmpIdList": { "type": "array", "items": { "type": "number" } },
    "copyEmpIdList": { "type": "array", "items": { "type": "number" } },
    "observerEmpIdList": { "type": "array", "items": { "type": "number" } },
    "endTime": { "type": "number" },
    "pushNow": { "type": "number", "default": 1 }
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
    "data": { "type": "number" }
  }
}
```

## 脚本映射
- `../../scripts/plan-create/create-simple.py`
