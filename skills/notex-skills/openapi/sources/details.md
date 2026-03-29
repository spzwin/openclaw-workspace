# GET https://notex.aishuo.co/noteX/openapi/notebooks/sources/details

## 作用

**Headers**
- `access-token`

**Query 参数（二选一）**
| 参数 | 说明 |
|---|---|
| `notebookId` | 目标 Notebook ID |
| `sourceId` | 目标 Source ID |

## 响应示例
```json
{
  "mode": "source",
  "notebook": { "id": "nb_001", "name": "产品规划" },
  "contexts": [
    { "id": "src_102", "name": "会议纪要" }
  ]
}
```

## 脚本映射

- `../../scripts/sources/source_index_sync.py`
