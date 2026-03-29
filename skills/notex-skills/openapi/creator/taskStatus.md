# GET https://notex.aishuo.co/noteX/openapi/trilateral/taskStatus/{taskId}

## 作用

**Headers**
- `access-token`

**Path 参数**
| 参数 | 必填 | 说明 |
|---|---|---|
| `taskId` | 是 | 任务 ID |

## 响应（关键字段示例）
```json
{
  "resultCode": 1,
  "data": {
    "task_status": "COMPLETED",
    "url": "https://notex.aishuo.co/?skillsopen=task-xxx"
  }
}
```

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
        "task_status": { "type": "string" },
        "url": { "type": "string" }
      }
    }
  }
}
```

## 轮询建议

- 60 秒一次，最多 20 次；超时后提示稍后查询。

## 脚本映射

- `../../scripts/creator/skills_run.py`
