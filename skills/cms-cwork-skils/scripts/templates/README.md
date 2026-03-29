# 脚本清单 — templates

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-list.py` | `POST /work-report/template/listTemplates` | 调用接口，输出 JSON 格式的事项列表 |
| `get-by-ids.py` | `POST /work-report/template/listByIds` | 按事项 ID 列表批量获取事项简易信息 |

## 使用方式

```bash
# 执行前需要预先准备好 appKey，并通过环境变量传入
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 执行脚本
python3 scripts/templates/get-list.py --limit 50
python3 scripts/templates/get-by-ids.py --template-ids 1001,1002

# 指定时间范围
python3 scripts/templates/get-list.py --begin-time 1735660800000 --end-time 1738339199000 --limit 50

# 需要精确获取事项详情时，可按 ID 列表查询
python3 scripts/templates/get-by-ids.py --body-json '[1001,1002]'
python3 scripts/templates/get-by-ids.py --body-file /path/to/template-ids.json
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

补充说明：
- `get-list.py` 默认跟随平台的最近时间窗口；如果返回空列表，可通过 `--begin-time/--end-time` 扩大范围
- 当平台返回 `data=null` 时，脚本会归一化为 `{"recentOperateTemplates":[]}`

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范，不包含登录发起逻辑
3. **入参定义以** `openapi/` 文档为准
