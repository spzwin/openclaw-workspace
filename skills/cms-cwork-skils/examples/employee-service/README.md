# employee-service 示例

## 模块说明
员工信息服务，支持批量员工信息查询和组织架构信息查询。

## 依赖脚本
- 批量员工：`../../scripts/employee-service/get-by-person-ids.py`
- 组织架构：`../../scripts/employee-service/get-org-info.py`

## 对应接口
- `POST /cwork-user/employee/getByPersonIds/{corpId}`
- `GET /cwork-user/employee/getEmployeeOrgInfo`

---

## 标准流程（含 3S1R 管理闭环）

### 场景一：批量获取员工信息

#### Step 1 — Suggest（建议）
```
建议：先确认 corpId 和 personId 列表，再批量拉取员工信息。
该接口适合把外部 personId 映射为当前企业下的员工对象。
```

#### Step 2 — Decide（确认/决策）
```
请确认：
□ corpId：____
□ personId 列表：____
```

#### Step 3 — Execute（执行）
执行批量员工查询脚本。

#### Step 4 — Log（留痕）
```
[LOG] employee-service.batch | corpId:xxx | count:N | ts:ISO8601
```

### 场景二：获取员工组织架构信息

#### Step 1 — Suggest（建议）
```
建议：当需要直属领导或二三级部门信息时，再调用组织架构查询。
```

#### Step 2 — Decide（确认/决策）
```
请确认：
□ empId：____
```

#### Step 3 — Execute（执行）
执行组织架构查询脚本。

#### Step 4 — Log（留痕）
```
[LOG] employee-service.org | empId:xxx | ts:ISO8601
```

---

## 输出格式

**批量员工信息：**
```json
{
  "resultCode": 1,
  "data": [
    {
      "id": "1514822127830339585",
      "name": "屈军利",
      "personId": 12139,
      "corpId": "1509805893730611201"
    }
  ]
}
```

**组织架构信息：**
```json
{
  "resultCode": 1,
  "data": {
    "empId": "1514822127830339585",
    "empName": "屈军利",
    "managerEmpName": "张成鹏",
    "secondLevelDeptName": "技术部",
    "thirdLevelDeptName": "开发组"
  }
}
```

---

## 注意事项
- `get-by-person-ids.py` 的输入是 `personId`，不是 `empId`
- `get-org-info.py` 的输入是 `empId`，适合补全上级与部门链路
- 两个接口都为只读查询，日志里应保留入参标识和返回数量
