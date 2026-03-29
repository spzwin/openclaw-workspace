# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/plugin/report/list

## 作用
获取插件场景下的最新待办列表与未读汇报列表聚合结果。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: application/json`

**JSON Body 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageIndex` | number | 否 | 页数从 1 开始，默认 1 |
| `pageSize` | number | 否 | 每页显示个数 |
| `lastUpdateTime` | number | 是 | 最后更新时间戳（毫秒），默认 0 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "pageIndex": { "type": "number", "default": 1 },
    "pageSize": { "type": "number", "default": 20 },
    "lastUpdateTime": { "type": "number", "default": 0 }
  },
  "required": ["lastUpdateTime"]
}
```

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
        "latestTodoList": { "type": "object" },
        "unreadReportList": { "type": "object" }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/plugin-report/get-list.py`
