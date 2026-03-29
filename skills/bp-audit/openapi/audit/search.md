# 搜索任务/分组

**接口**: 按名称模糊搜索任务和分组  
**描述**: 根据名称关键字快速定位任务或分组

---

## 接口 1：按名称模糊搜索任务

**基本信息**:
- **接口地址**: `/bp/task/v2/searchByName`
- **请求方式**: `GET`

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| groupId | string | 是 | 分组 ID |
| name | string | 是 | 任务名称关键字 |

**响应参数** `data` 类型为 `List<TaskSearchVO>`：

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 任务 ID |
| name | string | 任务名称 |
| groupId | string | 所属分组 ID |
| groupName | string | 所属分组名称 |
| type | string | 类型：`目标` / `关键成果` / `关键举措` |
| statusDesc | string | 任务状态 |
| reportCycle | string | 汇报周期 |
| planDateRange | string | 计划时间区间 |
| fullLevelNumber | string | 任务完整编码 |
| taskUsers | array | 任务参与人列表 |
| parentTask | object | 上级任务（父任务） |
| childTasks | array | 下级任务列表 |

**响应示例**:
```json
{
 "resultCode": 1,
 "resultMsg": null,
 "data": [
 {
 "id": "2001628713670279169",
 "name": "全栈交付项目模式探索",
 "groupId": "1993982002185506818",
 "groupName": "技术部",
 "type": "目标",
 "statusDesc": "进行中",
 "reportCycle": "doubleMonth+1",
 "planDateRange": "2025-01-07 ~ 2025-02-02",
 "fullLevelNumber": "A4-1",
 "taskUsers": [
 {
 "taskId": "2001628713670279169",
 "role": "承接人",
 "empList": [{ "id": "1512393131319586817", "name": "刘会芳" }]
 }
 ],
 "parentTask": null,
 "childTasks": [
 { "id": "2001628715230560258", "name": "AODW 工作方式的探索与实践", "type": "关键成果", "statusDesc": "进行中" }
 ]
 }
 ]
}
```

---

## 接口 2：按名称模糊搜索分组

**基本信息**:
- **接口地址**: `/bp/group/searchByName`
- **请求方式**: `GET`

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| periodId | string | 是 | 周期 ID |
| name | string | 是 | 分组名称关键字 |

**响应参数** `data` 类型为 `List<GroupSearchVO>`：

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 分组 ID |
| name | string | 分组名称 |
| periodId | string | 所属周期 ID |
| type | string | 类型：`org` = 组织节点，`personal` = 个人节点 |
| levelNumber | string | 层级编码 |
| employeeId | string | 员工 ID（个人类型时有效） |
| parentGroup | object | 上级分组 |
| childCount | integer | 下级分组数量 |

**响应示例**:
```json
{
 "resultCode": 1,
 "resultMsg": null,
 "data": [
 {
 "id": "1993982002185506818",
 "name": "技术部",
 "periodId": "1993981738711912449",
 "type": "org",
 "levelNumber": "A4",
 "employeeId": null,
 "parentGroup": {
 "id": "1993981993016758274",
 "name": "集团",
 "type": "org"
 },
 "childCount": 6
 }
 ]
}
```

---

## 审计用途

**快速定位审计对象**：

### 1. 任务搜索
- **专项审计**：搜索特定类型的任务（如含"收入"、"利润"的目标）
- **问题追踪**：搜索已知问题任务的名称关键字
- **承接分析**：通过 `parentTask`/`childTasks` 快速查看上下级关系

### 2. 分组搜索
- **部门定位**：快速找到目标部门的分组 ID
- **层级分析**：通过 `parentGroup`/`childCount` 了解组织层级
- **员工定位**：搜索员工姓名获取其个人分组 ID

### 3. 审计场景示例
```
场景：审计"技术部"的 BP 承接情况
1. 调用搜索分组：name="技术部" → 获取 groupId
2. 调用查询任务树：groupId=技术部 ID → 获取任务列表
3. 调用获取目标详情：逐个审计目标
```

---

## 脚本映射

无脚本，直接调用 API。
