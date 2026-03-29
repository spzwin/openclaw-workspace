# POST https://sg-cwork-api.mediportal.com.cn/im/skill/delete

## 作用

下架（删除）一个已发布的 Skill。

## Headers

| Header | 必填 | 说明 |
|---|---|---|
| `access-token` | 是 | 鉴权 token（依赖 `cms-auth-skills/common/auth.md` 获取） |
| `Content-Type` | 是 | `application/json` |

## 参数表（Query）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | integer(int64) | 否 | Skill ID |
| `delistReason` | string | 否 | 下架原因 |

> 注意：参数通过 URL Query String 传递，非 Body。

## 请求示例

``` 
POST /im/skill/delete?id=123&delistReason=已废弃
```

## 响应 Schema

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": true
}
```

## 脚本映射

- 执行脚本：`../../scripts/skill-management/delete_skill.py`
