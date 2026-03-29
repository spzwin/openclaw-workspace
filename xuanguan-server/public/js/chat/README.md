# Chat 模块说明（2.4）

## 目录职责

- `main.js`
  - 模块入口，只负责启动 `initUI()`
- `config.js`
  - 默认配置 + agentId 映射
  - 支持 `window.__XUANGUAN_CHAT_CONFIG__` 注入覆盖
- `state.js`
  - 单一状态源（会话、消息、未读、草稿、连接状态）
  - 本地存储 key 与联系人/草稿读写
- `api.js`
  - 认证、HTTP 请求、WS 连接、轮询封装
  - 请求超时控制（AbortController）
- `group-builder.js`
  - 建群成员拼装（内置 agent 勾选 + 自定义成员）
- `dto.js`
  - API DTO schema + 运行时校验（message/content/mentions/mentionTokens）
  - 校验失败自动降级兜底，不阻断页面渲染
- `mention.js`
  - `@` 候选交互（键盘/点击）
  - mentions 提取与 token 渲染
- `ui.js`
  - 视图渲染、事件绑定、消息发送、会话切换

---

## 配置项

### 默认配置
见 `config.js -> CHAT_CONFIG.defaults`：
- `apiUrl`
- `appId`
- `appSecret`
- `userId`

### agent 映射
见 `config.js -> CHAT_CONFIG.agents`：
- `coder`
- `researcher`
- `atlas`

可注入覆盖：
```html
<script>
window.__XUANGUAN_CHAT_CONFIG__ = {
  agents: {
    coder: { userId: 'agent_coder_real', display: '码爪' },
    researcher: { userId: 'agent_research_real', display: '研爪' },
    atlas: { userId: 'agent_atlas_real', display: 'Atlas' }
  }
};
</script>
```

未注入时自动回退默认值，保证本地可跑。

---

## Mentions 协议

发送消息时：
```json
{
  "content": {
    "type": "text",
    "text": "@coder 请看下这个问题",
    "mentions": [
      { "userId": "coder", "display": "码爪（coder）" }
    ],
    "mentionTokens": [
      { "type": "mention", "userId": "coder", "display": "码爪（coder）", "start": 0, "end": 6, "raw": "@coder" }
    ]
  }
}
```

渲染策略：
1. 优先使用 `mentionTokens` 做 token 渲染（不走纯文本替换）
2. 若只有 `mentions`（历史消息），从文本扫描构造 fallback token 再渲染
3. 若都没有，按普通文本渲染

---

## 扩展点

1. **消息类型扩展**
- 在 `ui.js -> renderMessageHtml` 增加 `image/file/card` 分支

2. **群组创建扩展**
- 在 `group-builder.js` 增加角色、权限字段

3. **提及策略扩展**
- 在 `mention.js -> extractMentions` 增加重复 mention 合并策略
- 在 `wireMention` 中支持 `@all`

4. **状态持久化扩展**
- `state.js` 可替换 localStorage 为 indexedDB

---

## 回归脚本

根目录可执行：
```bash
npm run chat:e2e
npm run chat:ui-e2e
```

- `chat:e2e`：API 级回归，覆盖创建群 -> @提及 -> 发送 -> 回显结构校验（mentions + mentionTokens）
- `chat:ui-e2e`：UI 点击流回归，覆盖创建群 -> @提及选择 -> 发送 -> 刷新回显 -> 会话切换草稿恢复

可通过环境变量覆盖：
- `CHAT_E2E_API_URL`
- `CHAT_E2E_APP_ID`
- `CHAT_E2E_APP_SECRET`
- `CHAT_E2E_USER_ID`
- `CHAT_E2E_AGENT_CODER / RESEARCHER / ATLAS`

## 错误码映射（api.js）

统一由 `assertApiOk/getUserError` 对外暴露用户文案，避免分叉。

已覆盖：
- `401` / token 相关 -> 鉴权失败
- `403` / permission-denied -> 无权限
- token-expired -> 登录过期
- timeout -> 请求超时
- network -> 网络连接失败

## 多标签同步（2.4）

使用 `BroadcastChannel + localStorage` 双通道同步：
- `draft-sync`：草稿实时同步
- `active-conversation`：活跃会话同步
- `unread-sync`：未读数同步
- `incoming-message`：新消息同步（跨标签回显）

打开多个标签页时，在一侧发送消息/切换会话，另一侧会自动同步状态。

## 性能优化（2.4）

### 虚拟滚动
- 联系人/会话/消息列表均使用 `renderVirtualList`
- 只渲染可视区域 + overscan 项
- 支持 1000+ 项不卡顿

### 大消息处理
- 超过 1200 字的消息自动折叠为 `<details>`
- 点击展开查看完整内容

## 无障碍（2.4）

### 键盘导航
- `Tab`：可达成交互元素
- `Enter`：确认选择（会话/联系人）
- `Esc`：关闭提及菜单
- `↑/↓`：切换提及候选
- `Ctrl/Cmd + Enter`：发送消息

### ARIA 属性
- 列表容器：`role="listbox"`
- 列表项：`role="option"` + `aria-label`
- 消息区：`role="log"` + `aria-live="polite"`

## 常见坑

1. **不要再用 inline onclick**
- 统一在 `ui.js -> bindEvents` 绑定事件
- 避免全局函数污染

2. **mentions 不要再做字符串 replace 高亮**
- 必须走 token 渲染，避免误替换和边界错误

3. **会话切换要同步草稿**
- 进入会话时读取 `draftKey(conversationId)`
- 输入事件实时保存草稿

4. **请求超时需可读提示**
- `api.js` 已统一超时错误文案，调用层不要吞异常
