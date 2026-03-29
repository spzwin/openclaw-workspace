# POST 分片转写列表

## 请求

```http
POST https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/splitRecordList
```

**Headers**

| 名称 | 必填 | 说明 |
|------|------|------|
| `appKey` | 是 | 见 `../common/appkey.md` |
| `Content-Type` | 是 | `application/json` |

**Body**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `meetingChatId` | string | 是 | 会议记录 ID（即列表接口的 `_id`） |

## 响应

- 分片列表在 `data` 中，每项含 `text`（转写文本）、`realTime` / `startTime`（时间，毫秒，相对会议开始或绝对时间戳，以实际返回为准）。
- 用于实时问答、按时间范围筛选内容、生成总结与待办。
