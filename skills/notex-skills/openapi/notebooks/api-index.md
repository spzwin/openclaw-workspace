# OpenAPI：Notebooks 模块索引

本模块接口一览：

1. `GET /openapi/notebooks/category-counts`
   - **作用**：按分类统计笔记本数量（含收藏、回收站、总计）。
   - **关键入参**：无
   - **关键返回**：各分类计数（`WORK_REPORT`/`KNOWLEDGE_BASE`/`AI_NOTES`/`AI_INTELLIGENCE`/`SHARED`/`MIXED`）及 `_total`
   - **鉴权**：Header `access-token`
   - **适用场景**：用户问"我有多少个笔记本"、"各分类有几个"
   - **详细文档**：`./category-counts.md`

2. `GET /openapi/notebooks`
   - **作用**：分页列出笔记本列表。
   - **关键入参**：`category`（分类筛选）、`favorite`（只看收藏）、`deleted`（回收站）、`page`/`pageSize`、`sort`、`type`（`owned`/`collaborated`/`all`）
   - **鉴权**：Header `access-token`
   - **适用场景**：用户要查看/浏览笔记本列表
   - **详细文档**：`./list.md`

3. `POST /openapi/notebooks`
   - **作用**：创建新笔记本。
   - **关键入参**：`title`（必填）、`category`（默认 `MIXED`）、`description`（可选）
   - **关键返回**：`data.notebookId`
   - **鉴权**：Header `access-token`
   - **详细文档**：`./create.md`

4. `POST /openapi/notebooks/{notebookId}/sources`
   - **作用**：向指定笔记本追加来源（Source）。
   - **关键入参**：Path `notebookId`（必填）、Body `title`/`type`（固定 `text`）/`content_text`（完整正文）
   - **关键返回**：`data.sourceId`
   - **鉴权**：Header `access-token`
   - **详细文档**：`./add-source.md`

5. `GET /openapi/notebooks/{notebookId}/sources`
   - **作用**：获取指定 Notebook 下的来源列表（不含正文 `contentText`）。
   - **关键入参**：Path `notebookId`（必填）；Query `businessType`（可选）
   - **关键返回**：来源列表（字段与 `/api/notebooks/{id}/sources` 一致）
   - **鉴权**：Header `access-token`
   - **详细文档**：`./sources-list.md`

6. `GET /openapi/notebooks/{notebookId}/sources/{sourceId}/content`
   - **作用**：获取来源完整正文（`contentText`）。
   - **关键入参**：Path `notebookId` / `sourceId`
   - **关键返回**：来源详情（含 `contentText`）
   - **鉴权**：Header `access-token`
   - **详细文档**：`./source-content.md`

脚本映射：
- `../../scripts/notebooks/notebooks_write.py`（创建 + 追加来源，可独立执行）
- `../../scripts/notebooks/notebooks_read.py`（来源列表 + 正文获取，可独立执行）
- 执行前请先阅读上方接口文档获取完整入参说明
