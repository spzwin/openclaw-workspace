# AppKey 使用说明（本技能统一鉴权）

本技能仅聚焦**实时会议**能力，鉴权仅涉及慧记会议 API。

## 读取规则

AppKey 的**读取顺序**以 `../../common/auth.md` 为准：

1. 环境变量 `XG_BIZ_API_KEY`
2. 上下文中的 `appKey` / `xgBizApiKey`
3. 用户提供的个人 AppKey（由调用方索取后传入）

脚本或代码中仅使用 1、2；第 3 步由 Agent/上层在未配置时向用户索取。

---

## 慧记会议 API

慧记会议列表、分片转写等接口在请求头中携带 AppKey：

**Headers**

| 名称 | 必填 | 说明 |
|------|------|------|
| `appKey` | 是 | 由上列读取规则得到 |
| `Content-Type` | 是 | `application/json; charset=utf-8` |

无需换 token，直接使用 AppKey 调用慧记接口。接口文档见 `../meeting/api-index.md`。
