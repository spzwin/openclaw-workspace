# ai-qa 示例

## 模块说明
针对指定汇报集合发起 AI SSE 问答，脚本会将 SSE 结果聚合后输出。

## 依赖脚本
`../../scripts/ai-qa/ask-sse.py`

## 对应接口
- `POST /work-report/open-platform/report/aiSseQaV2`

---

## 标准流程（含 3S1R 管理闭环）

### Step 1 — Suggest（建议）
**在发起问答之前，先给出建议方案。**

- 说明该接口是基于指定汇报内容做问答，不是通用知识库检索
- 建议问题尽量清晰、具体，避免开放式模糊查询
- 提示必须提供 `reportIdList`

```
建议：提问时尽量具体，避免过于宽泛的问题。
请先准备关联的 reportId 列表。
脚本内部会处理 SSE，并输出聚合后的 JSON 结果。
```

### Step 2 — Decide（确认/决策）
**涉及重要信息查询前，必须向用户确认问题。**

- 确认用户的问题表述是否清晰
- 确认是否已经提供 reportId 列表

```
请确认：
□ 您的问题：____
□ reportId 列表：____
□ 了解脚本会输出聚合后的 JSON：是
```

### Step 3 — Execute（执行）
执行 SSE 问答脚本。

### Step 4 — Log（留痕）
**问答结果必须完整记录。**

- 记录问题摘要、返回状态、时间戳
- 如果是多轮对话，需记录完整对话链
- 格式：`[LOG] ai-qa | question:xxx | ts:ISO8601 | status:success|error`

```
[LOG] ai-qa | question:如何创建周报 | ts:2026-03-25T13:57:00+08:00 | status:success
[LOG] ai-qa | question:如何创建周报（追问1）| ts:2026-03-25T13:58:00+08:00 | status:success
```

---

## 输出格式

```json
{
  "resultCode": 1,
  "data": {
    "answer": "这里是聚合后的 AI 回答",
    "eventCount": 6,
    "metrics": {
      "firstTextDelay": { "delay": 1200 },
      "costMoney": { "cost": 0.001 },
      "totalTimeCost": { "cost": 8000 }
    }
  }
}
```

---

## 注意事项
- 原始 OpenAPI 是 SSE，当前脚本会聚合后输出 JSON
- SSE 中的内容片段、耗时和费用事件会被拆开处理，`answer` 只保留聚合后的正文
- 同一会话内可多轮追问，但每次追问均需独立 Suggest → Decide → Log
- 日志需记录完整问答链，供追溯 AI 回答来源和质量评估
- 答案仅供参考，重要决策需人工核实
