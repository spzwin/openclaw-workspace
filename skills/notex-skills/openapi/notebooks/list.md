# GET https://notex.aishuo.co/noteX/openapi/notebooks

## 作用

**Headers**
- `access-token`

**Query 参数**
| 参数 | 说明 | 默认值 |
|---|---|---|
| `category` | 按分类筛选（`WORK_REPORT` / `KNOWLEDGE_BASE` / `AI_NOTES` / `AI_INTELLIGENCE` / `SHARED` / `MIXED` / `all`） | 不筛选 |
| `favorite` | 只看收藏（`true`/`false`） | `false` |
| `deleted` | 查看回收站（`true`/`false`） | `false` |
| `page` | 页码 | `1` |
| `pageSize` | 每页数量 | `50` |
| `sort` | 排序方式：`recent` / `title` / `created` | `recent` |
| `type` | 可见范围：`owned` / `collaborated` / `all` | `all` |

 