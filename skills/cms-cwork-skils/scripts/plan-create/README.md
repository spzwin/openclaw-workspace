# 脚本清单 — plan-create

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `create-simple.py` | `POST /work-report/open-platform/report/plan/create` | 调用接口，创建高级工作任务 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 执行脚本
python3 scripts/plan-create/create-simple.py \
  --main "开放平台测试-创建高级任务" \
  --needful "<p>任务要求</p>" \
  --target "<p>任务目标</p>" \
  --report-emp-ids 1512393035869810690 \
  --end-time 1774915200000
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
