# 一致性复核报告（2026-03-28）

## 结论
- 本次对 `27` 个脚本、`27` 份 `openapi` 接口文档、`15` 份 `examples`、`SKILL.md` 做了交叉一致性检查。
- 结果：结构一致、声明一致、参数说明一致，可用于 AI 组合调用。

## 检查范围
- `openapi/*/api-index.md` 与 `openapi/*/*.md` 的方法/路径/文档映射
- `openapi` 文档与 `scripts/*.py` 的 `API_URL`、HTTP 方法对齐
- `scripts/*/README.md` 与模块脚本集合、接口集合对齐
- `examples/*/README.md` 与模块脚本集合、接口集合对齐
- `examples` 是否具备 `对应接口 / 输出格式 / 注意事项` 三段
- 全量脚本 `--help` 探测能力（未注入 `appKey` 场景）
- `SKILL.md` 的数量统计与模块树一致性

## 核查结果
- 模块数：`15`
- API 文档：`27`
- Python 脚本：`27`
- 示例文档：`15`
- `--help` 探测失败脚本：`0`
- README 参数与脚本 `--help` 不一致：`0`

## 特殊说明
- `employee-service/get-by-person-ids` 使用路径模板 `/cwork-user/employee/getByPersonIds/{corpId}`。
  - 文档写法是模板路径；
  - 脚本实现是先定义基础 `API_URL`，再在调用时拼接 `/{corpId}`；
  - 这属于等价实现，不是不一致问题。

## 本轮加固项
- 在 `SKILL.md` 增加“AI 组合调用约束（推荐）”：
  - 显式参数优先
  - 写操作确认
  - 大结果裁剪策略
  - `unreadList` 分页异常认知
  - 统一输出契约
