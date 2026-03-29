# report-query 示例

## 模块说明
汇报维度的待办、未读与已读判断能力，服务于建议、决策、反馈等主业务场景。

## 依赖脚本
- 汇报待办：`../../scripts/report-query/get-todo-list.py`
- 汇报未读：`../../scripts/report-query/get-unread-list.py`
- 已读判断：`../../scripts/report-query/is-report-read.py`

## 对应接口
- `POST /work-report/reportInfoOpenQuery/todoList`
- `POST /work-report/reportInfoOpenQuery/unreadList`
- `GET /work-report/reportInfoOpenQuery/isReportRead`

---

## 标准流程（含 3S1R 管理闭环）

### Step 1 — Suggest（建议）
```
建议：涉及决策/建议/反馈时，优先查询 report-query/todoList，而不是通用 todoTask。
如果只是追查未读汇报，再使用 unreadList。
需要核验单个员工是否已读时，使用 isReportRead。
```

### Step 2 — Decide（确认/决策）
```
请确认：
□ 查询类型：todoList / unreadList / isReportRead
□ 分页：第____页，每页____条（列表查询时）
□ reportId / employeeId（已读判断时）：____
```

### Step 3 — Execute（执行）
执行对应汇报查询脚本。

### Step 4 — Log（留痕）
```
[LOG] report-query | mode:todoList | page:1 size:20 | ts:ISO8601
```

---

## 注意事项
- `todoList` 是“汇报待办”，不是通用任务待办
- `unreadList` 是“汇报未读”，不是收件箱总列表
- 全部接口均为只读查询

---

## 输出格式

**汇报待办 / 汇报未读列表：**
```json
{
  "resultCode": 1,
  "data": {
    "total": 10,
    "list": [
      {
        "reportId": "2037801532216434690",
        "main": "【BP审查通知】请确认您的个人BP审查报告及修改要求",
        "todoId": "2037801532245794817",
        "detail": {
          "needAction": "需要建议",
          "hasSubsequentDecision": false
        }
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "serverReturnedSize": 10,
    "clientLimit": 3,
    "clientReturnedSize": 3
  }
}
```

**已读判断：**
```json
{
  "resultCode": 1,
  "data": false
}
```

补充说明：
- `get-unread-list.py` 默认只处理前 `200` 条，最大只处理前 `500` 条
- 平台实测中 `unreadList` 可能忽略请求里的 `pageSize`，因此不要把脚本裁剪结果误认为服务端真实分页结果
