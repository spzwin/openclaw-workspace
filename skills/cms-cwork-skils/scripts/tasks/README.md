# 脚本清单 — tasks

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-page.py` | `POST /work-report/report/plan/searchPage` | 调用接口，输出 JSON 格式的工作任务列表 |
| `get-simple-plan-and-report-info.py` | `GET /work-report/report/plan/getSimplePlanAndReportInfo` | 获取单个任务的简易信息及关联汇报列表 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 执行脚本
python3 scripts/tasks/get-page.py --page-index 1 --page-size 20 --keyword 接口联调 --status 1
python3 scripts/tasks/get-simple-plan-and-report-info.py --plan-id 123456

# 需要完整筛选时，直接传完整 JSON 请求体
python3 scripts/tasks/get-page.py --body-json '{"pageIndex":1,"pageSize":20,"status":1,"reportStatus":1}'
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
