# 认证与鉴权（统一前置规则）

## 1. 鉴权入口

```http
GET https://cwork-web.mediportal.com.cn/user/login/appkey?appCode=cms_gpt&appKey={CWork Key}
```

**返回字段映射**：
- `data.xgToken` → Header `access-token`

接口文档：`../openapi/common/appkey.md`

## 2. 统一前置鉴权规则（强约束）

1. **优先级 1（环境变量）**：读取 `XG_USER_TOKEN`。存在则直接使用。
2. **优先级 2（上下文 token）**：若无环境变量，尝试从上下文中读取 `token` / `xgToken` / `access-token` 字段。
3. **优先级 3（CWork Key 换取）**：仍无 token 时，向用户索取 `CWork Key` 并调用鉴权接口。
4. **禁区**：禁止向用户索取或解释 token 细节。对外只暴露 **CWork Key 授权动作**。

## 3. 强约束

- 所有业务请求仅需传递 `access-token`（它是 CWork Key 授权后的唯一凭证）。
- 建议对鉴权结果做**会话级缓存**，避免重复换取。

## 4. 权限与生命周期（安全要求）

- **最小权限**：仅使用当前任务所需能力范围，不扩展权限范围。
- **权限白名单**：对外能力应按模块/接口/动作做白名单控制。
- **生命周期**：token 仅用于会话期内使用，过期需重新获取。
- **禁止落盘**：`access-token` 不得写入文件或日志，仅允许内存级缓存。
