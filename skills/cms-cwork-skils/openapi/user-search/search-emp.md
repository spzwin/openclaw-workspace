# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-user/searchEmpByName

## 作用

根据姓名模糊搜索全部员工，返回内部员工与外部联系人结果。工作协同场景通常使用 `inside.empList[].id` 作为后续接口中的 `empId`。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `searchKey` | string | 是 | 员工姓名关键词（如"张三"） |

## 请求 Schema
```json
{
 "$schema": "http://json-schema.org/draft-07/schema#",
 "type": "object",
 "required": ["searchKey"],
 "properties": {
 "searchKey": { "type": "string", "description": "搜索关键词" }
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
    "data": {
      "type": "object",
      "properties": {
        "inside": {
          "type": "object",
          "properties": {
            "empList": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "id": { "type": "number" },
                  "personId": { "type": "number" },
                  "name": { "type": "string" },
                  "title": { "type": "string" },
                  "mainDept": { "type": "string" }
                }
              }
            }
          }
        },
        "outside": {}
      }
    }
 }
}
```

## 脚本映射

- `../../scripts/user-search/search-emp.py`
