# tasks 示例

## 模块说明
获取工作任务分页索引，以及单个任务的简易信息与关联汇报列表。

## 依赖脚本
- 任务分页：`../../scripts/tasks/get-page.py`
- 任务简易信息：`../../scripts/tasks/get-simple-plan-and-report-info.py`

## 对应接口
- `POST /work-report/report/plan/searchPage`
- `GET /work-report/report/plan/getSimplePlanAndReportInfo`

---

## 标准流程（含 3S1R 管理闭环）

### Step 1 — Suggest（建议）
**在拉取任务列表之前，先给出建议方案。**

- 建议合适的分页参数（默认20条/页）
- 建议是否需要按任务状态（0 关闭 / 1 进行中）过滤
- 如需复杂筛选，可直接传完整 JSON 请求体

```
建议：默认拉取最近 20 条任务记录，按创建时间倒序。
如需按状态筛选，可补充 status 参数（0/1）。
如需更复杂筛选，可使用 body-json。
```

### Step 2 — Decide（确认/决策）
**涉及数据查询前，必须向用户确认参数。**

- 确认分页大小和页码
- 确认状态过滤条件（如适用）
- 确认是否使用高级筛选 JSON

```
请确认查询参数：
□ 分页：第____页，每页____条（默认第1页，20条）
□ 状态过滤：全部 / 0-关闭 / 1-进行中
□ 高级筛选 JSON（可选）：____
```

### Step 3 — Execute（执行）
执行任务列表查询脚本。

### Step 4 — Log（留痕）
**查询结果必须完整记录。**

- 记录查询参数、返回条数、时间戳
- 格式：`[LOG] tasks | page:1 size:20 status:all | result:N | ts:ISO8601`

```
[LOG] tasks | page:1 size:20 status:1 | result:8 | ts:2026-03-25T13:54:00+08:00
```

---

## 输出格式

**任务分页：**
```json
{
  "resultCode": 1,
  "data": {
    "total": 531,
    "pageNum": 1,
    "pageSize": 20,
    "list": [
      {
        "id": "2001963433511276546",
        "main": "GPTS后台管理会话中是否发送“开始”设置",
        "status": 1,
        "reportStatus": 3,
        "creatorName": "杨晶晶"
      }
    ]
  }
}
```

**任务简易信息：**
```json
{
  "resultCode": 1,
  "data": {
    "id": "2001963433511276546",
    "main": "GPTS后台管理会话中是否发送“开始”设置",
    "status": 1,
    "reportList": [
      {
        "id": "2011377694498947074",
        "main": "GPTS后台管理会话中是否发送“开始”设置",
        "writeEmpName": "伍孝权"
      }
    ]
  }
}
```

---

## 注意事项
- 任务状态本身不是通过本接口修改
- 查询为只读操作
- `getSimplePlanAndReportInfo` 适合在已知 `planId` 后追查该任务下的汇报链路
- 日志需保留查询参数与结果摘要，供后续分析
