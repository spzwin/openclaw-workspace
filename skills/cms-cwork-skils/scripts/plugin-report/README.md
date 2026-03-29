# 脚本清单 — plugin-report

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-list.py` | `POST /work-report/plugin/report/list` | 获取插件聚合结果，包含最新待办与未读汇报 |
| `get-latest-list.py` | `POST /work-report/plugin/report/latestList` | 获取插件场景下的最新待办列表 |
| `get-unread-list.py` | `POST /work-report/plugin/report/unreadList` | 获取插件场景下的未读汇报列表 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 获取聚合结果
python3 scripts/plugin-report/get-list.py --last-update-time 0 --page-index 1 --page-size 10

# 获取最新待办列表
python3 scripts/plugin-report/get-latest-list.py --last-update-time 0 --page-index 1 --page-size 10

# 获取未读汇报列表
python3 scripts/plugin-report/get-unread-list.py --last-update-time 0 --page-index 1 --page-size 10

# 复杂筛选可直接传完整 JSON 请求体
python3 scripts/plugin-report/get-list.py --body-json '{"pageIndex":1,"pageSize":10,"lastUpdateTime":0}'
python3 scripts/plugin-report/get-list.py --body-file /path/to/plugin-report.json
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
