# POST https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-file/uploadWholeFile

## 作用
上传本地文件，返回文件资源 ID。该 ID 可用于获取下载信息，也可在工作协同附件场景中作为 `fileId` 使用。

**鉴权类型**
- `appKey`

**Headers**
- `appKey`
- `Content-Type: multipart/form-data`

**Form Data 请求参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | file | 是 | 本地文件 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "file": { "type": "string" }
  },
  "required": ["file"]
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "resultMsg": { "type": ["string", "null"] },
    "data": { "type": "number" }
  }
}
```

## 脚本映射
- `../../scripts/file-service/upload-file.py`
