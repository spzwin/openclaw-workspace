# 脚本清单 — file-service

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `upload-file.py` | `POST /cwork-file/uploadWholeFile` | 上传本地文件并返回资源 ID |
| `get-download-info.py` | `GET /cwork-file/getDownloadInfo` | 获取文件下载链接与元信息 |

## 使用方式

```bash
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 推荐：显式参数名
python3 scripts/file-service/upload-file.py --file /path/to/file.png
python3 scripts/file-service/get-download-info.py --resource-id 123456789012345

# 兼容：旧的位置参数
python3 scripts/file-service/upload-file.py /path/to/file.png
python3 scripts/file-service/get-download-info.py 123456789012345
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- 支持 `-h/--help`，即使当前环境还未注入 `appKey`
- 推荐优先使用 `--file`、`--resource-id`

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
