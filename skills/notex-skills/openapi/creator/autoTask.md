# POST https://notex.aishuo.co/noteX/openapi/trilateral/autoTask

## 作用

> [!IMPORTANT]
> **素材完整性约束**：`sources` 列表中的 `content_text` 必须提供**完整原文**。任务生成（如 PPT、报告、视频等）完全基于此内容。任何摘要、内容缺失或片段截断都会直接导致生成产物质量下降或逻辑断层。

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body（必传字段）**
| 字段 | 类型 | 说明 | 约束 |
|---|---|---|---|
| `bizId` | string | 业务唯一标识 | 不可为空 |
| `bizType` | string | 业务类型 | 固定 `TRILATERA_SKILLS` |
| `title` | string | 标题 | 不可为空 |
| `skills` | string[] | 任务技能列表（`slide`/`report`/`mindmap`/`quiz`/`flashcards`/`infographic`/`video`/`audio`） | 不可为空 |
| `require` | string | 生成要求/风格 | 不可为空 |
| `sources` | object[] | 素材列表 | 不可为空 |

**sources 子字段**
| 字段 | 类型 | 说明 | 约束 |
|---|---|---|---|
| `id` | string | 素材 ID | 不可为空 |
| `title` | string | 素材标题 | 不可为空 |
| `content_text` | string | 素材正文 | **必须完整原文** |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["bizId", "bizType", "title", "skills", "require", "sources"],
  "properties": {
    "bizId": { "type": "string" },
    "bizType": { "type": "string", "const": "TRILATERA_SKILLS" },
    "title": { "type": "string" },
    "skills": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["slide", "infographic", "video", "audio", "report", "mindmap", "quiz", "flashcards"]
      },
      "minItems": 1
    },
    "require": { "type": "string" },
    "sources": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "title", "content_text"],
        "properties": {
          "id": { "type": "string" },
          "title": { "type": "string" },
          "content_text": { "type": "string" }
        }
      }
    }
  }
}
```

## 响应（关键字段）

- 返回 `taskId` 用于查询任务状态（字段位置以服务端返回为准）。

## 响应 Schema（简化）
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": {
      "type": "object",
      "properties": {
        "taskId": {
          "type": ["string", "array"]
        }
      },
      "additionalProperties": true
    }
  }
}
```

## 约束

- `sources[].content_text` 必须是完整原文，默认不允许摘要或截断。

## 脚本映射

- `../../scripts/creator/skills_run.py`
