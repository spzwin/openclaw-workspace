# 认证与鉴权（统一前置规则）

## 1. 鉴权入口

本技能仅使用**慧记会议 API**：请求头携带 `appKey`，见 `../openapi/common/appkey.md`。

## 2. 统一前置鉴权规则（强约束）

AppKey 读取顺序（与标准 skill 规范一致）：

1. **优先级 1（环境变量）**：读取 `XG_BIZ_API_KEY`。存在则作为本技能的 AppKey 使用（慧记请求头）。
2. **优先级 2（上下文）**：若无环境变量，从上下文中读取 `appKey` / `xgBizApiKey` 等字段。
3. **优先级 3（用户提供）**：仍无时，向用户索取 **个人 AppKey**。提示话术："你需要 AppKey 才能使用慧记会议功能。你可以在「工作协同」应用的设置中，从「个人 API 密钥」中获取你的个人 AppKey。" 再作为 AppKey 使用。
4. **禁区**：禁止向用户索取或解释 token 细节。对外只暴露 **个人 AppKey** 授权动作。

若运行环境已提供 `XG_USER_TOKEN`（access-token），且业务接口支持 token 鉴权，则优先使用 `XG_USER_TOKEN`，不再读取 AppKey。

## 3. 强约束

- 慧记会议列表/分片等接口：请求头携带 `appKey`（见 openapi）。无需换 token，直接使用 AppKey。

## 4. 权限与生命周期（安全要求）

- **最小权限**：仅使用当前任务所需能力范围。
- **禁止落盘**：`access-token`、AppKey 不得写入文件或日志，仅允许内存级缓存。
