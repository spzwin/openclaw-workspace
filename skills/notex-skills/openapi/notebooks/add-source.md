# POST https://notex.aishuo.co/noteX/openapi/notebooks/{notebookId}/sources

## 作用

> [!IMPORTANT]
> **内容完整性约束**：`content_text` 必须包含完整、无遗漏的正文内容（无论来源是文章原文、文件全量内容还是完整的上下文信息）。严禁提供摘要、截断或不完整的信息，这是确保生成质量的关键。

**Headers**
- `access-token`
- `Content-Type: application/json`

**Path 参数**
| 参数 | 必填 | 说明 |
|---|---|---|
| `notebookId` | 是 | 目标笔记本 ID |

**Body**
| 参数 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 来源标题 |
| `type` | 是 | 固定 `text` |
| `content_text` | 是 | 来源正文内容（必须完整） |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["title", "type", "content_text"],
  "properties": {
    "title": { "type": "string" },
    "type": { "type": "string", "const": "text" },
    "content_text": { "type": "string" }
  }
}
```

 

## 脚本映射

- `../../scripts/notebooks/notebooks_write.py`
