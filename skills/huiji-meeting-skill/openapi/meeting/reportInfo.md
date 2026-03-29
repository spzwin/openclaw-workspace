# POST 会议详情/报告 — reportInfo

## 完整接口

**URL（正确路径）**

```
POST https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/report/reportInfo
```

**请求头（Headers）**

| 名称 | 必填 | 说明 |
|------|------|------|
| `Content-Type` | 是 | `application/json` |
| `appKey` | 是 | 鉴权，见 `../common/appkey.md` 读取规则 |

**请求体（Body，JSON）**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `meetingChatId` | string | 是 | 会议记录 ID（与列表接口返回的 `_id` 一致） |

示例：

```json
{
  "meetingChatId": "<会议记录ID>"
}
```

**响应（出参）**

- **成功**：HTTP 200，body 示例：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "_id": "会议ID",
    "textReport": "# 会议标题\n\n报告正文 Markdown...",
    "textState": 2,
    "htmlReport": "<!DOCTYPE html>...",
    "htmlState": 2
  }
}
```

| 字段路径 | 类型 | 说明 |
|----------|------|------|
| `resultCode` | number | 1 表示成功 |
| `resultMsg` | string | 错误时文案 |
| `data` | object | 成功时存在 |
| `data._id` | string | 会议 ID |
| `data.textReport` | string | 会议结构化报告（Markdown），用于总结展示 |
| `data.textState` | number | 文本报告状态 |
| `data.htmlReport` | string | HTML 版报告（可选使用） |
| `data.htmlState` | number | HTML 报告状态 |

- **无权限**：HTTP 200，body 中业务码 401，无 `data`：

```json
{
  "resultCode": 401,
  "resultMsg": "no permission"
}
```

- **其他错误**：以 HTTP 状态码或 `resultCode` 非 1 表示，调用方需降级（如改用 checkSecondSttV2 或 splitRecordList）。

## 脚本与代码

- 调用：`MeetingClient.get_report_info(meeting_chat_id)`（见 `src/client.py`）
- 测试：可选运行 `scripts/test_report_info.py`（若该脚本存在）
