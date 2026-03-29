# GET https://notex.aishuo.co/noteX/openapi/notebooks/{notebookId}/sources

## 作用

获取指定 Notebook 下的来源列表（不含正文 `contentText`），支持按业务类型筛选。

**Headers**
- `access-token`

**Path 参数**
| 参数 | 必填 | 说明 |
|---|---|---|
| `notebookId` | 是 | 目标 Notebook ID |

**Query 参数（可选）**
| 参数 | 说明 |
|---|---|
| `businessType` | 业务类型筛选（可选） |

## 响应说明

- 返回来源列表，字段与 `/api/notebooks/{id}/sources` 一致。
- 正文 `contentText` 不返回；如需完整正文请调用 `source-content` 接口。

## 脚本映射

- `../../scripts/notebooks/notebooks_read.py`
