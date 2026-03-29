# 脚本清单 — user-search

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `search-emp.py` | `GET /cwork-user/searchEmpByName` | 根据姓名搜索员工 |

## 使用方式
```bash
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 推荐：显式参数名
python3 scripts/user-search/search-emp.py --keyword "张三"

# 兼容：旧的位置参数
python3 scripts/user-search/search-emp.py "张三"
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- 支持 `-h/--help`，即使当前环境还未注入 `appKey`
- 推荐优先使用 `--keyword`，减少多脚本组合调用时的位置参数歧义

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
