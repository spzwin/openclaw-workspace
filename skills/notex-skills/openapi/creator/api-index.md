# OpenAPI：Creator 模块索引

本模块接口一览：

1. `POST /openapi/trilateral/autoTask`
   - **作用**：投递异步创作任务，支持 `slide`/`video`/`audio`/`report`/`mindmap`/`quiz`/`flashcards`/`infographic` 八种形态。
   - **关键入参**：`bizId`（唯一标识）、`skills`（技能枚举数组）、`require`（风格/要求）、`sources[].content_text`（必须完整原文）
   - **关键返回**：`data.taskId`（用于后续轮询）
   - **鉴权**：Header `access-token`（由 openApiAuthMiddleware 统一处理）
   - **详细文档**：`./autoTask.md`

2. `GET /openapi/trilateral/taskStatus/{taskId}`
   - **作用**：轮询创作任务状态，获取终态链接。
   - **关键入参**：Path 参数 `taskId`
   - **关键返回**：`data.task_status`（`COMPLETED`/`FAILED`/处理中）、`data.url`（完成后的预览链接）
   - **鉴权**：Header `access-token`
   - **轮询建议**：60 秒/次，最多 20 次
   - **详细文档**：`./taskStatus.md`

脚本映射：
- `../../scripts/creator/skills_run.py`（可独立执行）
- 执行前请先阅读上方接口文档获取完整入参说明
