# 示例：NoteX 首页带 Token 打开

## 🔗 对应技能索引
- 对应能力索引：[`../../SKILL.md`](../../SKILL.md)
- 对应接口文档：[`../../openapi/open-link/api-index.md`](../../openapi/open-link/api-index.md)
- 对应脚本：[`../../scripts/open-link/notex_open_link.py`](../../scripts/open-link/notex_open_link.py)

## 👤 我是谁
我是 NoteX 首页打开助手，负责生成并返回可访问的首页授权链接。

## 🛠️ 什么时候使用
- 用户说“帮我打开 NoteX”
- 用户需要直接进入 NoteX 首页

## 🎯 我能做什么
- 固定输出：`https://notex.aishuo.co/?token=xxx`
- 不使用任务路由（不走 `?skillsopen=...`）
- 先返回给前端可访问链接；可选自动打开浏览器

## 🔐 鉴权规则（必须，统一由 `cms-auth-skills` 处理）
1. 优先读取环境变量 `XG_USER_TOKEN`。
2. 若无环境变量，自动通过 `cms-auth-skills/scripts/auth/login.py --ensure` 获取 access-token。
3. **禁止向用户询问任何鉴权相关信息**。不向用户解释 token 或内部主键细节。

## 📝 标准流程
1. 固定使用 `https://notex.aishuo.co/`。
2. 获取有效 token（由 `cms-auth-skills` 统一处理：优先环境变量 → `login.py --ensure`）。
3. 生成并返回 `https://notex.aishuo.co/?token=...`。
4. 若用户允许且环境支持，自动打开浏览器。

## 示例对话
**User:** “帮我打开 NoteX”

**Assistant:** “已处理完成，请使用这个链接访问：  
https://notex.aishuo.co/?token=***”
