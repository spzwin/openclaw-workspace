# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/reportInfoOpenQuery/todoList

## 作用
分页获取当前用户需要处理的汇报待办列表，主要用于建议、决策、反馈场景。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageIndex` | number | 否 | 页数从 1 开始，默认 1 |
| `pageSize` | number | 否 | 每页显示个数，默认 20 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "pageIndex": { "type": "number", "default": 1 },
    "pageSize": { "type": "number", "default": 20 }
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
- `../../scripts/report-query/get-todo-list.py`
