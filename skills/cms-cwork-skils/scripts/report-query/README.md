# 脚本清单 — report-query

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-todo-list.py` | `POST /work-report/reportInfoOpenQuery/todoList` | 获取汇报待办分页列表 |
| `get-unread-list.py` | `POST /work-report/reportInfoOpenQuery/unreadList` | 获取汇报未读分页列表 |
| `is-report-read.py` | `GET /work-report/reportInfoOpenQuery/isReportRead` | 判断指定员工是否已读某条汇报 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 获取汇报待办列表
python3 scripts/report-query/get-todo-list.py --page-index 1 --page-size 20

# 获取未读汇报列表
python3 scripts/report-query/get-unread-list.py --page-index 1 --page-size 20

# 判断是否已读
python3 scripts/report-query/is-report-read.py --report-id 123456 --employee-id 10001

# 复杂分页查询可直接传完整 JSON 请求体
python3 scripts/report-query/get-todo-list.py --body-json '{"pageIndex":1,"pageSize":20}'
python3 scripts/report-query/get-todo-list.py --body-file /path/to/report-query.json

# 返回体较大时，可在本地截断输出并同时落文件
python3 scripts/report-query/get-unread-list.py --page-index 1 --page-size 20 --client-limit 5 --output-file /tmp/unread.json
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- 默认只处理前 `200` 条；即使显式传更大值，脚本也最多只处理前 `500` 条
- `--client-limit` 只裁剪脚本最终输出，不改变平台真实返回
- `--output-file` 保存的是脚本裁剪后的输出结果，适合避免终端输出被截断
- 平台实测中 `unreadList` 可能忽略传入的 `pageSize`，因此脚本仍会在客户端补做裁剪

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
