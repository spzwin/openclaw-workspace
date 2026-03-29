# 脚本清单 — report-message

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `find-my-new-msg-list.py` | `GET /work-report/open-platform/report/findMyNewMsgList` | 获取我的新消息列表 |
| `read-report.py` | `GET /work-report/open-platform/report/readReport` | 标记汇报已读，并清理未读/新消息提醒 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 查询重要消息
python3 scripts/report-message/find-my-new-msg-list.py --msg-type 1

# 阅读汇报并清理提醒（有副作用）
python3 scripts/report-message/read-report.py --report-id 123456

# 新消息很多时，可限制终端输出并保存结果到文件
python3 scripts/report-message/find-my-new-msg-list.py --msg-type 1 --client-limit 5 --output-file /tmp/msg-list.json
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- `find-my-new-msg-list.py` 返回 `data.total` 与 `data.msgList`
- 当消息较多时，脚本会附带 `serverReturnedSize`、`clientLimit`、`clientReturnedSize`
- `read-report.py` 虽然是 `GET`，但它是状态变更接口，不应按只读接口理解

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
4. `find-my-new-msg-list.py` 默认只处理前 `200` 条，最大只处理前 `500` 条，并支持 `--client-limit/--output-file`
