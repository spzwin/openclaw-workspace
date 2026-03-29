# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/todoTask/listCreatedFeedbacks

## 作用
获取指定员工创建的反馈类型待办列表；不传 `empId` 时默认查询当前登录用户。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`

**Query 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `empId` | number | 否 | 反馈创建人员工 ID |

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "todoId": { "type": "number" },
          "reportId": { "type": "number" },
          "status": { "type": "number" },
          "type": { "type": "string" },
          "content": { "type": "string" }
        }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/todos/list-created-feedbacks.py`
