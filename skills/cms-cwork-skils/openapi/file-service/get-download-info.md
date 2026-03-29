# GET https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-file/getDownloadInfo

## 作用
根据资源 ID 获取临时下载链接和文件元信息。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `resourceId` | number | 是 | 文件资源 ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resourceId": { "type": "number" }
  },
  "required": ["resourceId"]
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
        "downloadUrl": { "type": "string" },
        "fileName": { "type": "string" },
        "resourceId": { "type": "number" },
        "suffix": { "type": "string" },
        "size": { "type": "number" }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/file-service/get-download-info.py`
