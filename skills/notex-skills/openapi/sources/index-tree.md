# GET https://notex.aishuo.co/noteX/openapi/notebooks/sources/index-tree

## 作用

**Headers**
- `access-token`

**Query 参数**
| 参数 | 说明 | 默认值 |
|---|---|---|
| `type` | `all` / `owned` / `collaborated` | `all` |

## 响应示例
```json
{
  "generatedAt": "2026-03-10T09:00:00.000Z",
  "tree": [
    {
      "id": "nb_001",
      "name": "产品规划",
      "sources": [
        { "id": "src_101", "name": "需求评审纪要" }
      ],
      "children": []
    }
  ]
}
```

## 脚本映射

- `../../scripts/sources/source_index_sync.py`
