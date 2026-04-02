---
name: cms-auth-skills
description: CMS 基础鉴权 Skill — 为所有上层 Skill 提供 appKey 和 access-token。**所有业务接口 header 中要求传入 appKey 或 access-token 的，都必须通过本 Skill 获取，严禁自行拼接或硬编码。** 用户提到登录、授权、鉴权、token、appKey、协同 key、CWork Key、刷新权限、重新授权，或遇到 401/403/权限不足/未授权时，优先触发本 Skill。
skillCode: cms-auth-skills
priority: 1
---

# cms基础 Skill — 授权基础层

**版本**: v2.3

> **⚠️ 重要：所有业务接口 header 中要求传入 `appKey` 或 `access-token` 的，都必须且只能通过本 Skill（`cms-auth-skills`）获取，严禁自行拼接、硬编码或通过其他方式获取鉴权值。**

## 定位

这是所有上层 Skill 都会依赖的 **最高优先级基础 Skill**（`priority: 1`，最先加载）。

所有上层 Skill 都应通过 `dependencies` 依赖本 Skill，不应各自复制一份登录鉴权逻辑。

这里的授权能力只做一件事：为上层 Skill 的业务接口准备好可用的鉴权值。

最终只返回两种结果：

- `appKey`
- `access-token`


## 能力总览

| # | 能力 | 脚本 | 需要 token |
|---|------|------|-----------| 
| 1 | 登录授权 / 获取 appKey / 获取 token | `scripts/auth/login.py` | 否 |

---

## 意图路由

| 用户说 | 执行 | token |
|---|---|---|
| "登录" / "获取 token" / "获取 access-token" / "重新授权" | `login.py --ensure` | 否 |
| "获取 appKey" / "获取 APPK" / "获取 APK" / "获取工作协同 key" / "获取协同 K" / "获取协同 key" / "获取 CWork Key" | `login.py --resolve-app-key` | 否 |

鉴权相关扩展意图：

- 用户提到"授权一下""拿一下授权 key""帮我取一下协同 key""帮我拿 appKey""帮我查一下工作协同 key"，都应优先路由到 `scripts/auth/login.py`
- 需要 `appKey` 时执行 `login.py --resolve-app-key`
- 需要 `access-token` 时执行 `login.py --ensure`

---

## 通用约束与约定

本节等同于原 `conventions.md` 总宪章。

### 1. 作用范围

- 本 Skill 只负责准备鉴权值
- 本 Skill 最终只返回两种结果：`appKey` 或 `access-token`
- 本 Skill 不负责七牛、Skill 安装、依赖检查等其他业务能力

### 2. 鉴权类型

所有业务接口都必须先看目标业务 Skill 的接口文档声明，再决定当前属于哪一种类型：

- `none` / `nologin`
- `appKey`
- `access-token`

如果接口是 `none` / `nologin`，直接调用，不走授权脚本。

### 3. context 规则

- 上层先判断登录方式，再把参数整理到 `context`
- `context` 统一使用顶层字段
- 建议只使用这几类字段：`appKey`、`access-token` / `token`、`account_id`、`send_id` / `sender_id`

**鉴权值获取的两条路径：**

| 条件 | 缓存 | 环境变量 | 自动获取（API） |
|------|------|----------|----------------|
| **有 `send_id` / `sender_id`** | ✅ 读取 + 写入 | ❌ 不读取 | ✅ 通过 `send_id` + `account_id` 自动获取 |
| **无 `send_id` / `sender_id`** | ❌ 不读取也不写入 | ✅ 读取 `XG_BIZ_API_KEY` / `XG_APP_KEY` / `XG_USER_TOKEN` | ❌ 不执行 |

- 有 `send_id` 时：优先缓存 → context → 自动获取（API），**不读取环境变量**
- 无 `send_id` 时：优先 context → 环境变量，**不读缓存**
- 环境变量读取兼容 Windows / macOS / Linux，读取异常时静默跳过，不会中断脚本

### 4. Header 与输出规则

- `appKey` 模式只传 `appKey`
- `access-token` 模式只传 `access-token`
- 可以给一个业务接口同时传 `appKey` 和 `access-token`
- `build_auth_headers()` 只负责返回鉴权 header，不附带其他通用 header
- 对用户只输出结论或必要提示，不在面向用户的消息中回显 `appKey`、`access-token`、内部主键（脚本通过 stdout 管道传递鉴权值不受此约束）
- 如果内部取值失败，直接跳到下一步，不向用户暴露中间缺失过程

### 5. 调用安全

- 所有接口调用必须有明确业务目标
- 出错时间隔 1 秒、最多重试 3 次
- 严禁无限循环重试
- 禁止在面向用户的日志、文件中明文展示 `access-token`（脚本通过 stdout 管道传递鉴权值不受此约束）

### 6. 脚本约束

- `scripts/` 下脚本必须使用 Python 编写
- `stdout` 输出结果，`stderr` 输出日志
- 零依赖 — 仅 Python 标准库

---

## 认证与鉴权规则

本节等同于原 `auth.md` 鉴权专项规则。

这个基础 Skill 的授权能力只负责两种结果：

- `appKey`
- `access-token`

无论内部怎么取值、怎么兜底，最终都是为了给业务接口准备这两类值之一。

### 1. AI 执行顺序

涉及鉴权的业务调用时，AI 必须按下面顺序执行：

1. 先读本文件（SKILL.md）
2. 再读目标业务 Skill 对应的 `openapi/*.md`
3. 判断业务接口类型：`none` / `nologin`、`appKey`、`access-token`
4. 按本文件规则准备 `context`
5. 如果需要鉴权，调用 `scripts/auth/login.py`
6. `login.py` 最终只返回 `appKey` 或 `access-token`
7. 拿到鉴权值后，再调用业务脚本或业务接口

### 2. 上层与 login.py 的职责边界

- 上层先判断接口是 `none` / `nologin`、`appKey` 还是 `access-token`
- 上层负责把可用参数整理到 `context` 后再传给 `login.py`

传给 `login.py` 的标准参数建议只有这几类：

- 均使用 `context` 的顶层字段
- `appKey`
- `access-token` 或 `token`
- `account_id`
- `send_id` / `sender_id`

**取值策略由 `send_id` 决定：**

- **有 `send_id`**：缓存 → context → 自动获取（API），不读环境变量
- **无 `send_id`**：context → 环境变量（`XG_BIZ_API_KEY` / `XG_APP_KEY` / `XG_USER_TOKEN`），不读缓存

### 3. 先看接口文档，再判断鉴权类型

执行具体业务前，先看目标业务 Skill 对应的 `openapi/*.md`，确认当前接口属于哪一种类型：

- `none` / `nologin`
- `appKey`
- `access-token`

> 不要先选脚本，再反推鉴权。顺序必须是：先看业务 `openapi`，再定鉴权类型，再准备参数，再调用脚本方法。

### 4. nologin / none 模式

当接口声明为 `none` 或 `nologin` 时：

- 不传 `appKey`
- 不传 `access-token`
- 直接调用接口

### 5. appKey 模式

当接口声明使用 `appKey` 时，Header 只传：

```http
appKey: {appKey}
```

处理顺序很简单：

1. 先看 `context.appKey`
2. 再尝试通过 `context.send_id` / `context.sender_id` + `context.account_id` 自动获取 `appKey`
3. 如果仍然没有，就向用户索要工作协同 key
4. 最终把 `appKey` 放到 header 里调用业务接口

### 6. access-token 模式

当接口声明使用 `access-token` 时，Header 只传：

```http
access-token: {token}
```

处理顺序也保持简单：

1. 先看 `context.access-token` / `context.token`
2. 如果还没有，就继续按 `appKey` 的逻辑去拿 `appKey`
3. 如果最终还拿不到 `appKey`，就向用户索要工作协同 key
4. 拿到 `appKey` 后，再由脚本内部换成 `access-token`
5. 最终把 `access-token` 放到 header 里调用业务接口

> `access-token` 模式下，内部可以先拿 `appKey` 再换 token，但最终对业务接口只传 `access-token`。

### 7. send_id / sender_id / account_id 自动获取规则

自动获取逻辑是脚本内部逻辑，只约束下面几点：

- 只有当 `context` 里同时存在有效的 `send_id` / `sender_id` 和 `account_id` 时，才允许执行自动获取逻辑
- 如果 `send_id` / `sender_id` 或 `account_id` 缺失，直接跳过自动获取逻辑
- `send_id` / `sender_id` 传空字符串、`null`、`None` 时，按缺失处理
- `account_id` 需要做映射后再参与 appKey 获取
- 具体映射规则、请求参数、接口地址，在脚本中维护
- 任一步骤取不到值时，直接进入下一步，不向用户回显内部取值过程
- 只有最终确实无法自动完成时，才向用户索要工作协同 key

### 8. 强约束

- **所有业务接口 header 中要求传入 `appKey` 或 `access-token` 的，都必须且只能通过本 Skill 的 `python3 login.py` 脚本获取，严禁自行拼接、硬编码或通过 `fetch`、`curl`、`urllib`、`requests` 等方式直接调用底层 HTTP 鉴权接口**
- 涉及鉴权的业务调用前，必须先读本文件
- 必须先判断接口是 `none` / `nologin`、`appKey` 还是 `access-token`
- 不要默认所有接口都走 `access-token`
- 不要给同一个业务接口同时传 `appKey` 和 `access-token`
- 有 `send_id` 时走缓存 + 自动获取，不读环境变量；无 `send_id` 时走环境变量，不读缓存
- 这个基础 Skill 的授权结果只有两类：`appKey` 或 `access-token`
- 环境变量读取兼容 Windows / macOS / Linux，异常时静默跳过
- 禁止在面向用户的日志、文件中明文展示 `access-token`（脚本通过 stdout 管道传递鉴权值不受此约束）

---

## 脚本调用方式

- 脚本不是"一脚本一接口"
- 先根据 `openapi/*.md` 判断本次接口的鉴权类型
- 再把本次需要的 `appKey` 或 `access-token` 解析出来
- 最后调用对应脚本里的具体方法
- `build_auth_headers()` 只负责返回鉴权 header，不附带其他通用 header

### nologin 接口

> 注：以下示例假设 `scripts/` 在 Python 模块搜索路径中。实际使用时，import 路径需根据项目结构和 `PYTHONPATH` 配置调整。

```python
from auth.login import build_auth_headers

headers = build_auth_headers("none")
```

### appKey 接口

```python
from auth.login import resolve_app_key, build_auth_headers

context = {
    "appKey": "...",
    "account_id": "...",
    "send_id": "...",
}

app_key = resolve_app_key(context=context)
headers = build_auth_headers("appKey", context=context)
```

### access-token 接口

```python
from auth.login import ensure_token, build_auth_headers

context = {
    "token": "...",
    "appKey": "...",
    "account_id": "...",
    "send_id": "...",
}

token = ensure_token(context=context)
headers = build_auth_headers("access-token", context=context)
```

---

## 缓存机制与命令行参数

### 缓存说明

- **仅当 `send_id` / `sender_id` 存在且有效时**，才启用缓存（读取 + 写入），以 `send_id` 为 key 存入 `cms-auth/auth.json`
- **无 `send_id` 时**，完全不涉及缓存，改为从环境变量获取鉴权值
- 使用 `--update` 参数可以强制跳过缓存，重新获取

### 命令行示例

```bash
# 获取 appKey
python login.py --resolve-app-key \
  --context-json '{"account_id": "...", "send_id": "..."}'

# 获取 access-token
python login.py --ensure \
  --context-json '{"appKey": "..."}'

# 强制重新获取（跳过缓存）
python login.py --ensure --update \
  --context-json '{"appKey": "...", "send_id": "..."}'
```


---

## 约束

1. **零依赖** — 仅 Python 标准库
2. **stdout = 结果，stderr = 日志** — 便于管道组合
3. **重试 3 次，间隔 1 秒** — 网络请求容错
4. **日志脱敏** — 日志中 token 值做脱敏处理

---

## 文件结构

```text
cms-auth-skills/
├── SKILL.md                            # 技能定义（本文件）
└── scripts/
    └── auth/login.py                   # appKey/token 解析 + 鉴权 header 组装
```
