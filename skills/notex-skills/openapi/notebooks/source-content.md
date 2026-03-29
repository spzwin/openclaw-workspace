# GET https://notex.aishuo.co/noteX/openapi/notebooks/{notebookId}/sources/{sourceId}/content

## 作用

获取某个来源的完整正文内容（`contentText`），用于需要原文的场景。

**Headers**
- `access-token`

**Path 参数**
| 参数 | 必填 | 说明 |
|---|---|---|
| `notebookId` | 是 | 目标 Notebook ID |
| `sourceId` | 是 | 目标 Source ID |

## 响应说明

- 返回来源详情，包含 `contentText` 正文（与 `/api/notebooks/{id}/sources/{sourceId}/content` 一致）。

## 脚本映射

- `../../scripts/notebooks/notebooks_read.py`
