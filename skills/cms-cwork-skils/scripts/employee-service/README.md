# 脚本清单 — employee-service

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-by-person-ids.py` | `POST /cwork-user/employee/getByPersonIds/{corpId}` | 批量获取员工信息 |
| `get-org-info.py` | `GET /cwork-user/employee/getEmployeeOrgInfo` | 获取员工组织架构信息 |

## 使用方式

```bash
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 推荐：显式参数名
python3 scripts/employee-service/get-by-person-ids.py --corp-id 123456 --person-ids "10001,10002"
python3 scripts/employee-service/get-org-info.py --emp-id 10001

# 兼容：旧的位置参数
python3 scripts/employee-service/get-by-person-ids.py 123456 "10001,10002"
python3 scripts/employee-service/get-org-info.py 10001
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- 支持 `-h/--help`，即使当前环境还未注入 `appKey`
- 推荐优先使用 `--corp-id`、`--person-ids`、`--emp-id`

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
