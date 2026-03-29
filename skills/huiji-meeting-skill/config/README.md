# 配置说明

- **default.json**：默认配置，可直接修改接口地址、缓存等。分发时已包含，无密钥。
- **appKey**：留空即可，运行时由环境变量 `XG_BIZ_API_KEY` 提供（优先级高于配置文件），避免密钥进仓库。
- **接口地址**：`apiBaseUrl`、`splitRecordUrl`、`checkSecondSttUrl`、`reportInfoUrl` 均可按环境修改，无需改代码。
- **local.json**（可选）：本地覆盖，已被 `.gitignore` 忽略，勿提交。
