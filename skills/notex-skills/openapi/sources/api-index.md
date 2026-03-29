# OpenAPI：Sources 模块索引

本模块接口一览：

1. `GET /openapi/sources/index-tree`
   - **作用**：拉取全量 Notebook + Source 索引树（仅 ID/名称，不含正文）。
   - **关键入参**：`type`（`all`/`owned`/`collaborated`，默认 `all`）
   - **关键返回**：`generatedAt`（生成时间）、`tree[]`（每项含 `id`/`name`/`sources[]`/`children[]`）
   - **鉴权**：Header `access-token`
   - **适用场景**：需要浏览/定位用户名下所有笔记本和来源时，先调此接口建立索引
   - **详细文档**：`./index-tree.md`

2. `GET /openapi/sources/details`
   - **作用**：按 `notebookId` 或 `sourceId`（二选一）获取最小详情（仅 ID + 名称）。
   - **关键入参**：Query `notebookId` 或 `sourceId`（二选一）
   - **关键返回**：`mode`（`notebook`/`source`）、`notebook`（`id`+`name`）、`contexts[]`（`id`+`name`）
   - **鉴权**：Header `access-token`
   - **适用场景**：已知 ID 后查对应笔记本或来源的名称定位信息
   - **详细文档**：`./details.md`

脚本映射：
- `../../scripts/sources/source_index_sync.py`（可独立执行）
- 执行前请先阅读上方接口文档获取完整入参说明
