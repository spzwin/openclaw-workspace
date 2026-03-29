# 脚本清单 — ai-qa

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `ask-sse.py` | `POST /work-report/open-platform/report/aiSseQaV2` | 调用接口，返回指定汇报集合的 SSE 问答结果 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 执行脚本
python3 scripts/ai-qa/ask-sse.py "请总结这几篇汇报的核心风险" "12345,67890"
```

## 输出说明

所有脚本的输出均为 **JSON 格式**，脚本会将 SSE 结果合并后输出。

补充说明：
- `data.answer` 只保留聚合后的正文
- `data.metrics` 会拆分保留 `firstTextDelay`、`costMoney`、`totalTimeCost`
- `data.eventCount` 表示本次聚合到的 SSE 事件数量

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
