# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/report/findMyNewMsgList

## 作用
获取当前用户的新消息汇总与明细列表。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`

**Query 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `msgType` | number | 否 | 消息类型过滤；文档默认 1，表示重要消息 |

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": {
      "type": "object",
      "properties": {
        "total": { "type": "number" },
        "msgList": { "type": "array" }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/report-message/find-my-new-msg-list.py`
