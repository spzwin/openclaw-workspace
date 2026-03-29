# POST 会议列表（分页）

## 请求

```http
POST https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/chatListByPage
```

**Headers**

| 名称 | 必填 | 说明 |
|------|------|------|
| `appKey` | 是 | 见 `../common/appkey.md` |
| `Content-Type` | 是 | `application/json; charset=utf-8` |

**Body**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `pageNum` | number | 是 | 页码，从 0 开始 |
| `pageSize` | number | 是 | 每页条数 |
| `sortKey` | string | 否 | 排序字段。为确保与技能输出一致（按创建时间倒序：最新在前），建议固定传 `createTime` |
| `nameBlur` | string | 否 | 名称模糊搜索 |
| `limit` | string | 否 | 可选 |

> 排序约束：为保证返回列表与 `SKILL.md` 中“按创建时间倒序（最新在前）”的展示规则一致，调用 `chatListByPage` 时应显式设置 `sortKey: "createTime"`（不要依赖服务端默认排序）。

## 响应

- 成功：`resultCode === 1`，列表在 `data.pageContent`（注意不是 `data.list`）。
- 单条字段：`_id`、`name`、`combineState`（0=进行中，2=已完成）、`createTime`、`finishTime`、`meetingLength`、`tidyText`、`simpleSummary`、`keywordList` 等。

详见技能说明中的「会议搜索与发现」与「字段映射」。
