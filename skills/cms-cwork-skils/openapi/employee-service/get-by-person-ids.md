# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-user/employee/getByPersonIds/{corpId}

## 作用
根据企业 ID 和 personId 列表批量查询员工信息。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**Path 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `corpId` | number | 是 | 企业 ID |

**JSON Body 请求参数**
请求体为 `Long[]`。

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": { "type": "number" }
}
```

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
          "id": { "type": "number" },
          "personId": { "type": "number" },
          "name": { "type": "string" },
          "dingUserId": { "type": "string" },
          "title": { "type": "string" }
        }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/employee-service/get-by-person-ids.py`
