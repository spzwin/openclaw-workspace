# ROUTING_V1（Main 中枢路由，非 sub-agent）

## 目标
- main 统一入口
- main 基础回答
- main 按意图转给常驻 agent 会话
- main 统一收口回复

## 路由表
- coder：代码、脚本、修 Bug、重构、工程实现
- researcher：信息检索、竞品对比、事实核验、总结报告
- atlas：bounty 机会筛选、收益优先级、变现路径

## 会话键
- `agent:coder:main`
- `agent:researcher:main`
- `agent:atlas:main`

## 派单模板（main -> 目标 agent）
- 任务目标：
- 原始用户请求：
- 约束（时间/预算/禁用项）：
- 输出格式：
- 完成标准（DoD）：

## 收口模板（main -> 用户）
1. 结论（先给结果）
2. 关键依据（2-4条）
3. 下一步（可执行）
4. 风险/待确认（如有）

## 失败兜底
- 目标会话异常/超时：main 直接接管
- 路由不确定：main 先问 1 个澄清问题
- 同一任务最多一次二次转派
