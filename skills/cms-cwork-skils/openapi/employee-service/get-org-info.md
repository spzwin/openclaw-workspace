# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-user/employee/getEmployeeOrgInfo

## 作用
根据员工 ID 获取直属领导和二三级部门等组织架构信息。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `empId` | number | 是 | 员工 ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "empId": { "type": "number" }
  },
  "required": ["empId"]
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
        "empId": { "type": "number" },
        "empName": { "type": "string" },
        "managerEmpId": { "type": "number" },
        "managerEmpName": { "type": "string" },
        "secondLevelDeptId": { "type": "number" },
        "secondLevelDeptName": { "type": "string" },
        "thirdLevelDeptId": { "type": "number" },
        "thirdLevelDeptName": { "type": "string" }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/employee-service/get-org-info.py`
