# POST https://notex.aishuo.co/noteX/openapi/notebooks

## 作用

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 参数 | 必填 | 说明 | 默认值 |
|---|---|---|---|
| `title` | 是 | 笔记本标题 | — |
| `category` | 否 | 分类枚举（`WORK_REPORT`/`KNOWLEDGE_BASE`/`AI_NOTES`/`AI_INTELLIGENCE`/`SHARED`/`MIXED`） | `MIXED` |
| `coverType` | 否 | 封面类型 | `icon` |
| `coverValue` | 否 | 封面图标 | `book` |
| `description` | 否 | 笔记本描述 | 空 |
| `parentNotebookId` | 否 | 父级笔记本 ID | 自动 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["title"],
  "properties": {
    "title": { "type": "string" },
    "category": { "type": "string" },
    "coverType": { "type": "string" },
    "coverValue": { "type": "string" },
    "description": { "type": "string" },
    "parentNotebookId": { "type": "string" }
  }
}
```
 
## 脚本映射

- `../../scripts/notebooks/notebooks_write.py`
