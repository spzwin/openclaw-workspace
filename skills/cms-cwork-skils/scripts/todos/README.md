# 脚本清单 — todos

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-list.py` | `POST /work-report/todoTask/todoList` | 调用接口，输出 JSON 格式的待办事项列表 |
| `complete.py` | `POST /work-report/open-platform/todo/completeTodo` | 调用接口，提交建议/决策并完成待办 |
| `list-created-feedbacks.py` | `GET /work-report/todoTask/listCreatedFeedbacks` | 获取用户创建的反馈类型待办列表 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 执行脚本
python3 scripts/todos/get-list.py --page-index 1 --page-size 20 --type feedback
python3 scripts/todos/complete.py 12345 --content "同意该方案" --operate agree
python3 scripts/todos/list-created-feedbacks.py --emp-id 10001
python3 scripts/todos/list-created-feedbacks.py --client-limit 5 --output-file /tmp/feedbacks.json

# 查询待办时如需额外字段，可直接传完整 JSON 请求体
python3 scripts/todos/get-list.py --body-json '{"pageIndex":1,"pageSize":20,"type":"feedback","executionResult":"待处理"}'
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- `list-created-feedbacks.py` 为平台全量查询接口，脚本默认只处理前 `200` 条，最大只处理前 `500` 条
- 返回较多时可用 `--client-limit/--output-file` 控制脚本输出

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
