# templates 示例

## 模块说明
获取最近处理过的事项列表，以及按 ID 批量获取事项简易信息，用于发起汇报时选择事项。

## 依赖脚本
- 最近事项列表：`../../scripts/templates/get-list.py`
- 事项批量详情：`../../scripts/templates/get-by-ids.py`

## 对应接口
- `POST /work-report/template/listTemplates`
- `POST /work-report/template/listByIds`

---

## 标准流程（含 3S1R 管理闭环）

### Step 1 — Suggest（建议）
**在拉取事项列表之前，先给出建议方案。**

- 说明返回的是“最近处理事项”，不是汇报模板库
- 建议按时间范围和 limit 控制返回结果
- 提示该接口是只读查询

```
建议：默认拉取最近 50 条事项列表。
如需限定范围，可传 beginTime / endTime。
事项列表仅用于发起汇报时选择事项，不涉及数据变动。
```

### Step 2 — Decide（确认/决策）
**涉及数据查询前，必须向用户确认参数。**

- 确认是否需要限定时间范围
- 确认返回条数上限

```
请确认：
□ limit：50（默认）/ 其他：____
□ 时间范围：默认最近一个月 / 自定义：____
```

### Step 3 — Execute（执行）
执行事项列表查询。

### Step 4 — Log（留痕）
**查询结果必须完整记录。**

- 记录查询条件、返回事项数量、时间戳
- 格式：`[LOG] templates | limit:50 | result:N | ts:ISO8601`

```
[LOG] templates | limit:50 | result:12 | ts:2026-03-25T13:56:00+08:00
```

---

## 输出格式

```json
{
  "resultCode": 1,
  "data": {
    "recentOperateTemplates": [
      {
        "templateId": 1001,
        "templateName": "市场周报"
      }
    ]
  }
}
```

---

## 注意事项
- 事项列表查询为只读操作
- `listByIds` 适合在已经拿到 `templateId` 后补充名称映射
- 日志需记录查询参数与返回数量
- 返回结果用于后续填写 `templateId`
