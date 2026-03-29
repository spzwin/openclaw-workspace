# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/todoTask/todoList

## 作用
分页查询当前用户待办列表（任务/签批/指引/反馈等）。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageIndex` | number | 否 | 页码（默认 1） |
| `pageSize` | number | 否 | 每页条数（默认 10） |
| `type` | string | 否 | 筛选类型 (plan-任务, sign-签批, lead-指引, feedback-反馈, file_audit-文件审核) |
| `executionResult` | string | 否 | 待办事项执行结果 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "pageIndex": { "type": "number", "default": 1 },
    "pageSize": { "type": "number", "default": 10 },
    "type": { "type": "string" },
    "executionResult": { "type": "string" }
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
- `../../scripts/todos/get-list.py`
