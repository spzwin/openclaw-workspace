# 脚本清单 — inbox

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-list.py` | `POST /work-report/report/record/inbox` | 调用接口，输出 JSON 结构化的收件箱汇报列表 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 执行脚本
python3 scripts/inbox/get-list.py --page-index 1 --page-size 20

# 需要高级筛选时，直接传完整 JSON 请求体
python3 scripts/inbox/get-list.py --body-json '{"pageIndex":1,"pageSize":20,"readStatus":0}'
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
