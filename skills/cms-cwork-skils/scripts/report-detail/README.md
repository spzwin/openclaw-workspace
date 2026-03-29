# 脚本清单 — report-detail

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-info.py` | `GET /work-report/report/info` | 调用接口，输出 JSON 格式的汇报结构详情 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 推荐：显式参数名
python3 scripts/report-detail/get-info.py --report-id 2037895527831597058

# 兼容：旧的位置参数
python3 scripts/report-detail/get-info.py 2037895527831597058
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- 支持 `-h/--help`，即使当前环境还未注入 `appKey`
- 推荐优先使用 `--report-id`

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
