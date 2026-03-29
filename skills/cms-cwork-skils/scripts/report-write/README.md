# 脚本清单 — report-write

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `submit.py` | `POST /work-report/report/record/submit` | 发送汇报 |
| `reply.py` | `POST /work-report/report/record/reply` | 回复汇报 |

## 使用方式

```bash
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 简单模式：发送汇报
python3 scripts/report-write/submit.py \
  --main "本周工作进展" \
  --content-html "<p>已完成接口联调</p>" \
  --accept-emp-ids 10001,10002

# 完整模式：从文件读取请求体
python3 scripts/report-write/submit.py --body-file ./submit-body.json

# 简单模式：回复汇报
python3 scripts/report-write/reply.py \
  --report-record-id 1234567890 \
  --content-html "已收到，我会在今天下班前给出方案"

# 完整模式：直接传完整 JSON
python3 scripts/report-write/reply.py --body-json '{"reportRecordId":"1234567890","contentHtml":"已处理"}'
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
