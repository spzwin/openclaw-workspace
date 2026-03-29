# report-write 示例

## 模块说明
发送汇报与回复汇报，构成工作协同主链路中的核心写操作。

## 依赖脚本
- 发送汇报：`../../scripts/report-write/submit.py`
- 回复汇报：`../../scripts/report-write/reply.py`

## 对应接口
- `POST /work-report/report/record/submit`
- `POST /work-report/report/record/reply`

---

## 标准流程（含 3S1R 管理闭环）

### 场景一：发送汇报（数据变动操作 ⚠️）

#### Step 1 — Suggest（建议）
**涉及数据变动前，必须先给出建议并说明影响。**

```
建议：先确认汇报标题、正文和接收链路。
如需附件，请先调用 file-service 上传文件，获取 fileId 后再放入 fileVOList。
若需要建议/决策流程，请优先使用 reportLevelList，而不是只传 acceptEmpIdList。
```

#### Step 2 — Decide（确认/决策）
**数据变动前，必须获取用户明确决策。**

```
⚠️ 确认执行发送汇报：
□ 标题：____
□ 正文：____
□ 接收人/流程节点：____
□ 附件 fileId（可选）：____
□ 输入 "确认提交" 以继续：____
```

#### Step 3 — Execute（执行）
执行发送汇报脚本。

#### Step 4 — Log（留痕）
**数据变动结果必须完整记录。**

```
[LOG] report-write.submit | reportId:xxx | title:xxx | ts:ISO8601 | operator:user
```

### 场景二：回复汇报（数据变动操作 ⚠️）

#### Step 1 — Suggest（建议）
**涉及数据变动前，必须先给出建议并说明影响。**

```
建议：先确认要回复的 reportRecordId 和回复内容。
如需附件，同样先上传文件，再把 fileId 放入 mediaVOList。
如果要提醒原汇报人，保持 sendMsg=true。
```

#### Step 2 — Decide（确认/决策）
**数据变动前，必须获取用户明确决策。**

```
⚠️ 确认执行回复汇报：
□ reportRecordId：____
□ 回复内容：____
□ 是否带附件：是 / 否
□ 输入 "确认回复" 以继续：____
```

#### Step 3 — Execute（执行）
执行汇报回复脚本。

#### Step 4 — Log（留痕）
**数据变动结果必须完整记录。**

```
[LOG] report-write.reply | reportRecordId:xxx | replyId:xxx | ts:ISO8601 | operator:user
```

---

## 输出格式

**发送汇报：**
```json
{
  "resultCode": 1,
  "data": {
    "id": "2037895527831597058"
  }
}
```

**回复汇报：**
```json
{
  "resultCode": 1,
  "data": 2037895545128869890
}
```

---

## 注意事项
- `submit.py`、`reply.py` 都是写操作，必须先走 Suggest → Decide → Execute → Log
- 如需附件，必须先通过 `file-service/upload-file.py` 拿到 `fileId`
- 简单模式适合常见场景；复杂链路请优先使用 `--body-json` 或 `--body-file`
