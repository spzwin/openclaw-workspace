# API 索引 — meeting（慧记会议）

接口列表：

1. **会议列表分页** — `POST` 会议列表（分页、排序、可选关键词）
   - 文档：`./chatListByPage.md`
2. **分片转写列表** — `POST` 获取指定会议的实时/历史转写分片
   - 文档：`./splitRecordList.md`
3. **会议详情/报告** — `POST` 获取会议结构化报告（`/ai-huiji/report/reportInfo`）
   - 文档：`./reportInfo.md`

鉴权：请求头携带 `appKey`，见 `../common/appkey.md`。

脚本与示例：`../../examples/meeting/README.md`、根目录 `main.py`。
