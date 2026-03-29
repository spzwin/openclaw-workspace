# OpenAPI：Open-Link 模块索引

本模块接口一览：

1. `NoteX 首页链接（带 token）`
   - **作用**：生成带 token 的 NoteX 首页授权链接，格式为 `https://notex.aishuo.co/?token=xxx`。
   - **关键入参**：无新增业务 API；token 由 `cms-auth-skills` 统一提供（环境变量 `XG_USER_TOKEN` → `login.py --ensure`）
   - **关键返回**：完整授权 URL（仅此模块允许返回带 token 的链接）
   - **适用场景**：用户说"帮我打开 NoteX"、"给我 NoteX 的链接"
   - **详细文档**：`./home-link.md`

脚本映射：
- `../../scripts/open-link/notex_open_link.py`（可独立执行）
- 执行前请先阅读上方接口文档获取完整入参说明
