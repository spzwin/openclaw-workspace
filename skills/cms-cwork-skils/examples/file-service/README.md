# file-service 示例

## 模块说明
文件服务能力，支持上传本地文件和获取下载链接。

## 依赖脚本
- 上传：`../../scripts/file-service/upload-file.py`
- 下载信息：`../../scripts/file-service/get-download-info.py`

## 对应接口
- `POST /cwork-file/uploadWholeFile`
- `GET /cwork-file/getDownloadInfo`

---

## 标准流程（含 3S1R 管理闭环）

### 场景一：上传文件

#### Step 1 — Suggest（建议）
```
建议：先上传本地文件获取 resourceId。
若后续要在工作协同中作为附件引用，可将该 resourceId 作为 fileId 使用。
```

#### Step 2 — Decide（确认/决策）
```
请确认：
□ 本地文件路径：____
□ 是否用于工作协同附件：是 / 否
```

#### Step 3 — Execute（执行）
执行文件上传脚本。

#### Step 4 — Log（留痕）
```
[LOG] file-service.upload | file:xxx | resourceId:xxx | ts:ISO8601
```

### 场景二：获取下载链接

#### Step 1 — Suggest（建议）
```
建议：使用 resourceId 拉取临时下载链接。
下载 URL 有效期通常为 1 小时。
```

#### Step 2 — Decide（确认/决策）
```
请确认：
□ resourceId：____
□ 了解下载链接为临时链接：是
```

#### Step 3 — Execute（执行）
执行下载信息查询脚本。

#### Step 4 — Log（留痕）
```
[LOG] file-service.download | resourceId:xxx | ts:ISO8601
```

---

## 输出格式

**文件上传：**
```json
{
  "resultCode": 1,
  "data": "2037895404074434561",
  "resultMsg": null
}
```

**下载信息：**
```json
{
  "resultCode": 1,
  "data": {
    "resourceId": "2037895404074434561",
    "fileName": "README.md",
    "suffix": "md",
    "size": 1926,
    "downloadUrl": "https://..."
  }
}
```

---

## 注意事项
- `upload-file.py` 返回的资源 ID 可直接作为工作协同附件里的 `fileId`
- `get-download-info.py` 返回的是临时下载链接，不适合长期持久化引用
- 上传与下载信息查询都依赖有效 `appKey`，但只有上传会产生新资源记录
