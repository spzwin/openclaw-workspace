# report-detail 示例

## 模块说明
根据 reportId 获取单篇汇报的完整结构化详情。

## 依赖脚本
`../../scripts/report-detail/get-info.py`

## 对应接口
- `GET /work-report/report/info`

---

## 标准流程（含 3S1R 管理闭环）

### Step 1 — Suggest（建议）
**在拉取汇报详情之前，先给出建议方案。**

- 说明该接口的用途：获取指定汇报的完整内容
- 提示需要有效的 reportId（通常从 inbox/outbox 列表中获取）
- 建议如果获取失败时的备选路径（如 reportId 已失效）

```
建议：使用从 inbox/outbox 获取的 reportId 查询汇报详情。
该接口为只读，不修改任何数据。
如 reportId 无效，将返回错误，建议通过列表接口重新获取有效 ID。
```

### Step 2 — Decide（确认/决策）
**涉及数据查询前，必须向用户确认操作。**

- 确认目标 reportId 是否有效、可信
- 确认是否了解该汇报的内容范围（附件、评论等）

```
请确认：
□ 目标 reportId：____（用户从列表中选取）
□ 已了解该操作仅查询数据，不涉及修改
```

### Step 3 — Execute（执行）
执行详情查询脚本。

### Step 4 — Log（留痕）
**查询结果必须完整记录。**

- 记录 reportId、查询时间、汇报标题摘要
- 格式：`[LOG] report-detail | reportId:xxx | ts:ISO8601 | title:...`

```
[LOG] report-detail | reportId:RPT-20260325001 | ts:2026-03-25T13:53:00+08:00 | title:三月第二周工作计划
```

---

## 输出格式

```json
{
  "resultCode": 1,
  "data": {
    "reportId": "2037895527831597058",
    "content": "测试开头：工作协同脚本联调，请忽略。",
    "createTime": "2026-03-28T14:12:11.000+00:00",
    "replies": [
      {
        "replyId": "2037895545128869890",
        "replyEmpName": "宋培众",
        "content": "<p>测试回复：工作协同脚本联调。</p>"
      }
    ]
  }
}
```

---

## 注意事项
- 必须使用有效的 reportId，无效ID会报错
- 详情查询不产生任何数据变更
- 日志需记录完整汇报标识，供后续引用或追溯
