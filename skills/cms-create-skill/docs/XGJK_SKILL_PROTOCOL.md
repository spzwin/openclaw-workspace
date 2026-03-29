# XGJK Skill 包协议规范 v1.06

本文档是一份**自包含的协议规范**。任何 AI 或开发者只需阅读本文档，即可从零创建一个符合 XGJK 标准的完整 Skill 包，无需额外的模板文件夹。

**全文结构**：

| 章节 | 内容 | 作用 |
|---|---|---|
| 一、目录结构规范 | Skill 包的物理结构、角色定义、依赖关系 | 定义"长什么样" |
| 二、各文件格式规范 | 每种文件的标准格式模板 | 定义"怎么写" |
| 三、标准创建流水线 | 5 步创建流程（骨架→SKILL.md→逐个API→索引→反思检查） | 定义"怎么造" |
| 四、验证清单 | A-H 共 8 节逐项检查 | 定义"怎么验" |
| 附录 A-C | 鉴权依赖规则、安装方式、SKILL 依赖片段 | 定义"如何依赖 cms-auth-skills" |
| 附录 D | 快速参考卡片 | 一览表 |
| 附录 E | 完整迷你示例（1 模块 1 接口） | 定义"最终产物长什么样" |

---

## 一、目录结构规范

一个完整的 Skill 包必须包含以下目录和文件：

```
<skill-name>/
├── SKILL.md                             # 主索引（能力宪章 + 能力树 + 路由表）
├── openapi/
│   └── <module>/                        # 每个业务模块一个目录
│       ├── api-index.md                 # 本模块接口索引
│       └── <endpoint>.md                # 每个接口一个独立文档
├── examples/
│   └── <module>/
│       └── README.md                    # 使用说明与触发条件
└── scripts/
    └── <module>/
        ├── README.md                    # 脚本清单
        └── <endpoint>.py                # 每个接口对应一个 Python 脚本
```

**强制规则**：
- `<module>` 替换为实际模块名（如 `robot`、`message`）
- `<endpoint>` 替换为实际接口名（如 `register-private`、`delete-my-robot`）
- 所有占位符（`<xxx>`）在最终产物中**不允许存在**
- 所有脚本**必须为 Python**（`.py`），禁止其他语言
- 每个 `openapi/<module>/<endpoint>.md` 都**必须有对应的** `scripts/<module>/<endpoint>.py`

### 1.1 各目录的角色定义

| 目录 | 角色 | 职责 | 内容性质 |
|---|---|---|---|
| `openapi/` | **文档层** | 定义每个接口"是什么"：URL、参数、Schema、响应 | **动态**，根据业务生成 |
| `scripts/` | **执行层** | 定义每个接口"怎么调"：Python 脚本调 API | **动态**，根据业务生成 |
| `examples/` | **引导层** | 定义"什么时候用"：触发条件、标准流程 | **动态**，根据业务生成 |
| `SKILL.md` | **索引层** | 统领全局：能力宪章、路由表、能力树、依赖声明 | **动态**，根据业务生成 |
| `cms-auth-skills` | **基础授权层** | 提供统一鉴权规则、授权接口文档与登录能力 | **外部依赖**，由目标 Skill 通过 `dependencies` 引入 |

### 1.2 各目录之间的依赖关系

```
SKILL.md（索引层）
  │
  ├── dependencies → cms-auth-skills   ← 基础授权层
  │                        │
  │                        ├── 引用 → cms-auth-skills/common/conventions.md
  │                        ├── 引用 → cms-auth-skills/common/auth.md
  │                        └── 引用 → cms-auth-skills/openapi/auth/*.md
  │
  └── 路由 → openapi/<module>/api-index.md（文档层 — 模块入口）
                │
                └── 列出 → openapi/<module>/<endpoint>.md（文档层 — 接口详情）
                              │
                              ├── "脚本映射" 指向 → scripts/<module>/<endpoint>.py（执行层）
                              │                        │
                              │                        ├── 需要鉴权时依赖 → cms-auth-skills
                              │                        └── 入参定义来自 → openapi/<module>/<endpoint>.md
                              │
                              └── 对应 → examples/<module>/README.md（引导层）
```

### 1.3 核心绑定规则（1:1）

**适用范围**：仅限 `openapi/<module>/` 下的业务接口文档。

| 文档层（定义） | 执行层（实现） | 绑定关系 |
|---|---|---|
| `openapi/<module>/<endpoint>.md` | `scripts/<module>/<endpoint>.py` | **1:1 强绑定** |

- `endpoint.md` 的"脚本映射"节 → 必须指向 `../../scripts/<module>/<endpoint>.py`
- `endpoint.py` 的入参字段 → 必须与 `endpoint.md` 中的参数表完全一致
- `endpoint.py` 的 API 路径 → 必须与 `endpoint.md` 中的 URL 一致
- `endpoint.py` 的 `AUTH_MODE`、请求头与鉴权环境变量 → 必须与 `endpoint.md` 中声明的"鉴权类型"完全一致

**说明**：授权接口文档统一由外部依赖 `cms-auth-skills/openapi/auth/*.md` 提供，不在目标 Skill 内重复生成。

### 1.4 依赖文件与动态文件

| 路径 | 性质 | 来源 | 说明 |
|---|---|---|---|
| `SKILL.md` 中的 `dependencies: - cms-auth-skills` | **固定要求** | 附录 A-C | 所有需要鉴权能力的 Skill 都必须声明此依赖 |
| `cms-auth-skills/common/*` | **外部依赖** | 由 `cms-auth-skills` 提供 | 基础层：鉴权规范与通用约束 |
| `cms-auth-skills/openapi/auth/*` | **外部依赖** | 由 `cms-auth-skills` 提供 | 授权接口参考文档 |
| 其余所有文件 | **动态** | 根据业务需求生成 | 受 1:1 绑定规则约束 |

> **`cms-auth-skills/openapi/auth/` vs `openapi/<module>/`**：前者提供统一授权接口说明，后者存放目标 Skill 的业务接口文档；业务文档仍受 1:1 绑定规则和脚本完整性检查约束。

### 1.5 鉴权最小原则

为避免未来各个 Skill 再次分叉出多套登录逻辑，目标 Skill 必须遵守以下最小原则：

1. **目标 Skill 只声明业务接口的鉴权要求，不实现登录流程**。
2. **每个 `openapi/<module>/<endpoint>.md` 都必须明确写出一个且仅一个鉴权类型**：`nologin`、`appKey`、`access-token` 三选一。
3. **每个 `scripts/<module>/<endpoint>.py` 只负责读取已准备好的鉴权值并调用业务 API**，不负责获取 `appKey`，也不负责换取 `access-token`。
4. **禁止生成本地鉴权层**：不生成 `common/auth.md`、`common/conventions.md`、`openapi/common/appkey.md`、`scripts/auth/login.py`。
5. **所有获取 `appKey` / `access-token` 的动作统一由 `cms-auth-skills` 承担**。

---

## 二、各文件格式规范

### 2.1 SKILL.md — 主索引

Skill 包的入口文件。只描述"能做什么"和"去哪里读"，**不写具体接口参数**。

```markdown
---
name: <skill-name>
description: <一句话描述>
skillcode: <skill-code>
dependencies:
  - cms-auth-skills
---

# <Skill 名称> — 索引

本文件提供**能力宪章 + 能力树 + 按需加载规则**。详细参数与流程见各模块 `openapi/` 与 `examples/`。

**当前版本**: v0.1

**接口版本**: <如：所有业务接口统一使用 `/openapi/*` 前缀，并按具体接口声明使用 `nologin`、`appKey` 或 `access-token` 鉴权。>

**能力概览（N 块能力）**：
- `<module-a>`：<能力摘要>
- `<module-b>`：<能力摘要>

统一规范：
- 认证与鉴权：`cms-auth-skills/common/auth.md`
- 通用约束：`cms-auth-skills/common/conventions.md`

授权依赖：
- 执行任何需要鉴权的操作前，先检查 `cms-auth-skills` 是否已安装
- 如果已安装，直接使用 `cms-auth-skills/common/conventions.md`、`cms-auth-skills/common/auth.md`、`cms-auth-skills/openapi/auth/appkey.md`、`cms-auth-skills/openapi/auth/login.md`
- 如果未安装，先执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续执行需要鉴权的操作

输入完整性规则（强制）：
1. <根据业务填写>
2. <根据业务填写>

建议工作流（简版）：
1. 读取 `SKILL.md` 与 `cms-auth-skills/common/*`，明确能力范围、鉴权与安全约束。
2. 识别用户意图并路由模块，先打开 `openapi/<module>/api-index.md`。
3. 确认具体接口后，加载 `openapi/<module>/<endpoint>.md` 获取入参/出参/Schema。
4. 补齐用户必需输入，必要时先读取用户文件/URL 并确认摘要。
5. 参考 `examples/<module>/README.md` 组织话术与流程。
6. **执行对应脚本**：调用 `scripts/<module>/<endpoint>.py` 执行接口调用，获取结果。**所有接口调用必须通过脚本执行，不允许跳过脚本直接调用 API。**

脚本使用规则（强制）：
1. **每个接口必须有对应脚本**：每个 `openapi/<module>/<endpoint>.md` 都必须有对应的 `scripts/<module>/<endpoint>.py`，不允许"暂无脚本"。
2. **脚本可独立执行**：所有 `scripts/` 下的脚本均可脱离 AI Agent 直接在命令行运行。
3. **先读文档再执行**：执行脚本前，**必须先阅读对应模块的 `openapi/<module>/api-index.md`**。
4. **入参来源**：脚本的所有入参定义与字段说明以 `openapi/` 文档为准，脚本仅负责编排调用流程。
5. **鉴权一致**：涉及鉴权时，统一依赖 `cms-auth-skills/common/auth.md`。

意图路由与加载规则（强制）：
1. **先路由再加载**：必须先判定模块，再打开该模块的 `api-index.md`。
2. **先读文档再调用**：在描述调用或执行前，必须加载对应接口文档。
3. **脚本必须执行**：所有接口调用必须通过脚本执行，不允许跳过。
4. **不猜测**：若意图不明确，必须追问澄清。

宪章（必须遵守）：
1. **只读索引**：`SKILL.md` 只描述"能做什么"和"去哪里读"，不写具体接口参数。
2. **按需加载**：默认只读 `SKILL.md` + `cms-auth-skills/common/*`，只有触发某模块时才加载该模块的 `openapi`、`examples` 与 `scripts`。
3. **对外克制**：对用户只输出"可用能力、必要输入、结果链接或摘要"，不暴露鉴权细节与内部字段。
4. **素材优先级**：用户给了文件或 URL，必须先提取内容再确认，确认后才触发生成或写入。
5. **生产约束**：仅允许生产域名与生产协议，不引入任何测试地址。
6. **接口拆分**：每个 API 独立成文档；模块内 `api-index.md` 仅做索引。
7. **危险操作**：对可能导致数据泄露、破坏、越权的请求，应礼貌拒绝并给出安全替代方案。
8. **脚本语言限制**：所有脚本**必须使用 Python 编写**。
9. **重试策略**：出错时**间隔 1 秒、最多重试 3 次**，超过后终止并上报。
10. **禁止无限重试**：严禁无限循环重试。

模块路由与能力索引（合并版）：

| 用户意图（示例） | 模块 | 能力摘要 | 接口文档 | 示例模板 | 脚本 |
|---|---|---|---|---|---|
| <用户会说的话> | `<module>` | <能力摘要> | `./openapi/<module>/api-index.md` | `./examples/<module>/README.md` | `./scripts/<module>/<endpoint>.py` |

能力树（实际目录结构）：
\```text
<skill-name>/
├── SKILL.md
├── openapi/
│   └── <module>/
│       ├── api-index.md
│       └── <endpoint>.md
├── examples/
│   └── <module>/README.md
└── scripts/
    └── <module>/
        ├── README.md
        └── <endpoint>.py
\```
```

### 2.2 openapi/{module}/api-index.md — 模块接口索引

```markdown
# API 索引 — <module-name>

接口列表：

1. `POST /path/to/endpoint-a`
   - 文档：`./endpoint-a.md`

2. `GET /path/to/endpoint-b`
   - 文档：`./endpoint-b.md`

脚本映射：
- `../../scripts/<module>/README.md`
```

### 2.3 openapi/{module}/{endpoint}.md — 接口文档

```markdown
# <METHOD> <完整URL>

## 作用

<结合业务场景的接口描述>

**鉴权类型**
- `<nologin | appKey | access-token>`

**Headers**
- `<根据鉴权类型填写实际 Header；如为 nologin 则写 无>`
- `Content-Type: application/json`

**Body**（或 **Query 参数**）
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `fieldA` | string | 是 | 字段说明 |
| `fieldB` | number | 否 | 字段说明 |

## 请求 Schema
\```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["fieldA"],
  "properties": {
    "fieldA": { "type": "string" },
    "fieldB": { "type": "number" }
  }
}
\```

## 响应 Schema
\```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": { "type": "object" }
  }
}
\```

## 脚本映射

- `../../scripts/<module>/<endpoint>.py`
```

### 2.4 examples/{module}/README.md — 使用说明

```markdown
# <模块名> — 使用说明

## 什么时候使用

- <用户实际的触发场景描述>

## 标准流程

1. 鉴权预检
2. 调用接口（通过脚本执行）
3. 输出结果摘要
```

### 2.5 scripts/{module}/README.md — 脚本清单

```markdown
# 脚本清单 — <module-name>

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `<endpoint>.py` | `POST /path/to/endpoint` | 调用接口，输出 JSON 结果 |

## 使用方式

\```bash
# 如接口是 nologin，无需设置鉴权环境变量

# 如接口使用 access-token
export XG_USER_TOKEN="your-access-token"

# 如接口使用 appKey
export XG_BIZ_API_KEY="your-app-key"
# 或 export XG_APP_KEY="your-app-key"

# 执行脚本
python3 scripts/<module>/<endpoint>.py
\```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **入参定义以** `openapi/` 文档为准
```

### 2.6 scripts/{module}/{endpoint}.py — 接口脚本

每个接口都必须有一个对应的 Python 脚本，模式固定：

```python
#!/usr/bin/env python3
"""
<模块名> / <接口名> 脚本

用途：调用 <接口描述>

使用方式：
  python3 scripts/<module>/<endpoint>.py

环境变量：
  无（当接口使用 nologin 时）
  XG_USER_TOKEN              — access-token（当接口使用 access-token 时）
  XG_BIZ_API_KEY / XG_APP_KEY — appKey（当接口使用 appKey 时）
  以上鉴权值建议由 cms-auth-skills 预先准备
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/<module>/<endpoint>.md 中声明的一致）
API_URL = "https://<生产域名>/<实际接口路径>"
AUTH_MODE = "access-token"  # 可选值：access-token / appKey / nologin；必须与 endpoint.md 的“鉴权类型”一致


def build_headers() -> dict:
    """根据鉴权模式构造请求头"""
    headers = {"Content-Type": "application/json"}

    if AUTH_MODE == "access-token":
        token = os.environ.get("XG_USER_TOKEN")
        if not token:
            print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
            sys.exit(1)
        headers["access-token"] = token
    elif AUTH_MODE == "appKey":
        app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
        if not app_key:
            print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
            sys.exit(1)
        headers["appKey"] = app_key

    return headers


def call_api() -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    # 请求体（根据实际接口字段填写）
    body = json.dumps({
        "fieldA": "value"
    }).encode("utf-8")

    req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    # 1. 调用接口，获取原始 JSON
    result = call_api()

    # 2. 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

**关键约束**：
- `AUTH_MODE` 必须与 `endpoint.md` 中声明的"鉴权类型"一致
- `access-token` 接口读取环境变量 `XG_USER_TOKEN`
- `appKey` 接口读取环境变量 `XG_BIZ_API_KEY` 或 `XG_APP_KEY`
- `nologin` 接口不读取鉴权环境变量
- 业务脚本不得实现获取 `appKey` / `access-token` 的登录逻辑，也不得直接调用授权接口
- `API_URL` 硬写完整 URL（含域名），必须与对应 `endpoint.md` 中声明的 URL 一致
- 必须有 `main()` 函数和 `if __name__ == "__main__"` 守卫
- 必须能独立在命令行运行

---

## 三、标准创建流水线

按以下 5 个步骤顺序执行，不可跳步、不可合并、不可省略。

### 开工前必备信息（未收集完毕禁止进入步骤 1）

在开始创建之前，必须先确认以下信息。**缺任何一项都不要开始。**

```
□ Skill 名称（英文，如 im-robot）：_______________
□ Skill 描述（一句话）：_______________
□ 生产域名（如 api.example.com）：_______________
  └─ 未提供则在 API_URL 中用 {待确认域名} 占位并提醒用户
□ 模块列表：
  └─ 模块 1 名称：_______________ 包含 ___ 个 API
  └─ 模块 2 名称：_______________ 包含 ___ 个 API
  └─ ...
□ 每个 API 的关键信息：
  └─ HTTP 方法（GET/POST）+ 完整路径 + 必填字段 + 响应关键字段
```

### 文件计数公式

在创建过程中和验证时，用此公式核对文件总数：

```
总文件数 = 1（SKILL.md）+ M × 3（每个模块的 api-index.md + examples/README.md + scripts/README.md）+ N × 2（每个 API 的 endpoint.md + endpoint.py）

其中：M = 模块数量，N = 所有模块的 API 总数
```

**示例**：1 个模块、3 个 API → `1 + 1×3 + 3×2 = 10 个文件`

> **⚠️ 创建完成后，数一下实际文件数，必须与公式结果一致。不一致说明有遗漏或多余。**

---

### 步骤 1：创建目录骨架 + 明确授权依赖

**先搭骨架，再填内容。此步骤纯机械操作，不涉及业务判断。**

#### 1a. 创建目录结构

```bash
mkdir -p <skill-name>/openapi/<module>      # 每个业务模块
mkdir -p <skill-name>/examples/<module>
mkdir -p <skill-name>/scripts/<module>
```

#### 1b. 明确授权依赖要求

目标 Skill 不再创建本地鉴权文件，统一依赖 `cms-auth-skills`：

| 序号 | 内容来源 | 写入路径 |
|---|---|---|
| 1 | 附录 A | 目标 `SKILL.md` 的 YAML 头写入 `dependencies: - cms-auth-skills` |
| 2 | 附录 B | 目标 `SKILL.md` 中引用 `cms-auth-skills/common/conventions.md` 与 `cms-auth-skills/common/auth.md` |
| 3 | 附录 C | 如需授权接口参考，引用 `cms-auth-skills/openapi/auth/appkey.md` 与 `cms-auth-skills/openapi/auth/login.md` |
| 4 | 本章 1.5 | 不创建本地 `scripts/auth/login.py`，也不在业务脚本中实现登录流程 |

不再创建 `<skill-name>/common/auth.md`、`<skill-name>/common/conventions.md`、`<skill-name>/openapi/common/appkey.md`、`<skill-name>/scripts/auth/login.py`。

#### ✅ 步骤 1 自检关卡（必须全部通过才能进入步骤 2）

```
□ 目录结构是否已全部创建？（openapi/<module>/, examples/<module>/, scripts/<module>/）
□ 是否已明确目标 Skill 统一依赖 cms-auth-skills？
□ 是否确认不会创建本地 common/auth.md、common/conventions.md、openapi/common/appkey.md、scripts/auth/login.py？
```

> **⚠️ 不通过则停下修复，禁止带病进入步骤 2。**

---

### 步骤 2：生成 SKILL.md

按本文档 **§2.1** 的格式，结合业务需求生成 `SKILL.md`，必须包含：

1. YAML 头部（`name` + `description` + `skillcode`）
2. YAML 头部中的 `dependencies: - cms-auth-skills`
3. 能力宪章（规则边界）
4. 能力概览（各模块能力摘要）
5. 建议工作流（标准使用流程）
6. 脚本使用规则
7. 意图路由表（用户意图 → 模块 → 文档 → 脚本）
8. 能力树（完整目录结构，必须与实际文件一一对应）

要结合业务场景重新组织语言，不是模板填充。

#### ✅ 步骤 2 自检关卡（必须全部通过才能进入步骤 3）

```
□ SKILL.md 是否有 YAML 头部（name + description + skillcode）？
□ SKILL.md 的 YAML 头是否包含 dependencies: - cms-auth-skills？
□ SKILL.md 是否包含能力宪章？
□ SKILL.md 是否包含能力概览（列出所有模块）？
□ SKILL.md 是否包含"授权依赖"安装指引（cms-auth-skills 的检查与安装说明）？
□ SKILL.md 是否包含建议工作流（6 步标准流程）？
□ SKILL.md 是否包含脚本使用规则？
□ SKILL.md 是否包含意图路由表（用户意图 → 模块 → 文档 → 脚本）？
□ SKILL.md 是否包含能力树（目录结构）？
□ 能力概览中的模块名是否与步骤 1 创建的 openapi/<module>/ 目录一致？
□ 路由表中引用的文件路径是否全部使用相对路径？
```

> **⚠️ 不通过则停下修复，禁止带病进入步骤 3。**

---

### 步骤 3：逐个 API 循环生成

**一个 API 完成全套再进入下一个。不允许"先批量写文档，再批量写脚本"。**

假设共有 N 个 API，按以下循环执行：

```
for 第 i 个 API (i = 1 到 N):
  │
  ├─ ① 写接口文档  openapi/<module>/<endpoint>.md
  │    按 §2.3 格式：作用、鉴权类型、Headers、参数表、请求Schema、响应Schema、脚本映射
  │
  ├─ ② 写执行脚本  scripts/<module>/<endpoint>.py
  │    按 §2.6 标准模式：先读取 endpoint.md 的“鉴权类型” → 读取对应环境变量 → API_URL 硬写 → 构造请求 → 调API → 输出结果
  │    入参字段必须与 ① 的参数表完全一致
  │
  └─ ③ 补充触发场景到  examples/<module>/README.md
       触发条件、标准流程、用户实际会说的话

  → 第 i 个 API 的迷你自检（2 项全过才进入下一个）：
     □ endpoint.md 的 URL 与 endpoint.py 的 API_URL 是否完全一致？
     □ endpoint.md 的参数表字段 与 endpoint.py 的请求 body 字段是否完全一致？
     □ endpoint.md 的鉴权类型 / Headers 与 endpoint.py 的 AUTH_MODE / 鉴权 Header 是否完全一致？

  → 第 i 个 API 完成，进入第 i+1 个
```

#### ✅ 步骤 3 自检关卡（所有 API 完成后，必须全部通过才能进入步骤 4）

```
□ 每个 openapi/<module>/<endpoint>.md 是否都有对应的 scripts/<module>/<endpoint>.py？（1:1 绑定）
□ 每个脚本是否都有 API_URL 硬写完整 URL？
□ 对需要鉴权的脚本，是否都按接口声明读取对应鉴权值？（appKey → XG_BIZ_API_KEY/XG_APP_KEY；access-token → XG_USER_TOKEN）
□ 每个脚本是否都有 main() 函数和 if __name__ == "__main__" 守卫？
□ examples/<module>/README.md 是否已补充所有 API 的触发场景？
□ 是否存在"有文档没脚本"或"有脚本没文档"的情况？（必须为零）
```

> **⚠️ 不通过则停下修复，禁止带病进入步骤 4。**

---

### 步骤 4：生成索引文件

所有 API 完成后，生成各模块的索引（放最后写，内容最完整最准确）：

1. **`openapi/<module>/api-index.md`**（按 §2.2 格式）— 接口清单 + 文档路径 + 脚本映射
2. **`scripts/<module>/README.md`**（按 §2.5 格式）— 脚本清单 + 共享依赖 + 使用方式

#### ✅ 步骤 4 自检关卡（必须全部通过才能进入步骤 5）

```
□ 每个模块是否都有 openapi/<module>/api-index.md？
□ 每个模块是否都有 scripts/<module>/README.md？
□ api-index.md 中列出的接口文档是否全部存在？
□ api-index.md 中列出的脚本路径是否全部存在？
□ scripts/README.md 中列出的脚本是否全部存在？
□ 索引中的接口数量是否与实际文件数量一致？
```

> **⚠️ 不通过则停下修复，禁止带病进入步骤 5。**

---

### 步骤 5：强制反思检查

创建完成后，必须执行三轮检查，不可跳过。

#### 5a. 第一轮：逐项核对验证清单

按本文档**第四章验证清单（A-H 全部 8 节）**，逐条核对每一项：

1. 对每一条给出 ✅ 或 ❌ 的明确判定，**不允许笼统地说"全部通过"**
2. 发现问题立即修复，修改后重新验证该项
3. 输出 A-H 各节检查结果汇总

#### 5b. 第二轮：交叉验证一致性（必须输出具体证据）

> **⚠️ 关键要求**：不能只说"通过"，必须列出具体证据。弱模型最常犯的错就是在这里直接写"全部通过"而没有真正检查。

1. **文件计数**：列出公式计算值和实际文件清单，逐一比对
   ```
   公式：1 + M×3 + N×2 = ？
   实际文件清单：（逐一列出每个文件名）
   是否一致：是/否
   ```
2. **1:1 绑定**：列出每一对 endpoint.md ↔ endpoint.py 的对应关系
   ```
   openapi/xxx/aaa.md ↔ scripts/xxx/aaa.py  ✅
   openapi/xxx/bbb.md ↔ scripts/xxx/bbb.py  ✅
   ...
   ```
3. **能力树一致**：将 SKILL.md 中的能力树与实际目录逐行比对，列出差异
4. **占位符清除**：在所有文件中搜索 `<module>`、`<endpoint>`、`<skill-name>` 等占位符，列出搜索结果
5. **入参校验**：列出每个脚本的 JSON body 字段，与对应 endpoint.md 的参数表逐一比对
6. **鉴权一致性**：列出每个 endpoint.md 的鉴权类型，与对应 endpoint.py 的 `AUTH_MODE` 和鉴权环境变量逐一比对

#### 5c. 第三轮：与参考示例结构比对

对照本文档**附录 E 的完整示例**，检查生成的 Skill 包是否具有相同的结构特征：

```
□ 目录层级是否与示例一致？（openapi/<module>/, examples/<module>/, scripts/<module>/）
□ SKILL.md 是否包含示例中的所有必备节（宪章、概览、工作流、路由表、能力树）？
□ 每个 endpoint.md 是否包含示例中的所有必备节（作用、Headers、参数表、请求Schema、响应Schema、脚本映射）？
□ 每个 endpoint.py 是否遵循示例中的脚本结构（docstring → import → API_URL → call_api → main → 守卫）？
□ api-index.md 和 scripts/README.md 是否与示例格式一致？
```

#### 5d. 最终裁决

三轮全部通过：
```
✅ 三轮反思审查完成：
- 第一轮验证清单 A-H：全部通过（逐项列出）
- 第二轮交叉验证：全部通过（附具体证据）
- 第三轮结构比对：与参考示例结构一致
- 文件计数：公式值 X = 实际值 X
- 共 X 个文件，Y 个接口，Z 个脚本
所有约束规则满足。
```

有不通过项且无法修复：
```
❌ 反思检查发现问题：[具体描述]，需人工确认后处理。
```

---

### 常见错误警告（弱模型高频踩坑清单）

> 以下是 AI 模型在生成 Skill 包时最容易犯的错误，请在每一步都保持警惕：

| # | 常见错误 | 正确做法 |
|---|---|---|
| 1 | 忘记在目标 `SKILL.md` 的 YAML 头声明 `dependencies: - cms-auth-skills` | 所有需要统一鉴权的 Skill 都必须声明这个依赖 |
| 2 | 继续生成本地 `common/auth.md`、`common/conventions.md`、`openapi/common/appkey.md`、`scripts/auth/login.py` | 目标 Skill 不再维护本地鉴权层与本地登录脚本，统一依赖 `cms-auth-skills` |
| 3 | `endpoint.md` 不声明"鉴权类型"，只在 Headers 里含糊带过 | 每个业务接口文档都必须明确写一个且仅一个鉴权类型：`nologin` / `appKey` / `access-token` |
| 4 | 脚本中用环境变量存储 API 地址（如 `os.environ.get("API_URL")`） | `API_URL` 必须硬写在脚本中；鉴权值只按接口声明从 `XG_USER_TOKEN` 或 `XG_BIZ_API_KEY/XG_APP_KEY` 读取 |
| 5 | 不区分 `nologin`、`appKey`、`access-token`，把所有接口都写成同一种鉴权 | 先读 `endpoint.md` 的鉴权类型，再决定脚本读取哪种鉴权值 |
| 6 | 在业务脚本里实现 `get_app_key` / `get_token` 或直接调用授权接口 | 业务脚本只调用业务 API，所有登录与授权获取动作统一交给 `cms-auth-skills` |
| 7 | 先批量写所有 endpoint.md，再批量写所有 endpoint.py | 必须一个 API 一个 API 来：endpoint.md → endpoint.py → examples，完成一个再下一个 |
| 8 | endpoint.md 中的 URL 和 endpoint.py 中的 `API_URL` 不一致 | 两者必须**完全相同**，写完后立即比对 |
| 9 | SKILL.md 能力树与实际目录结构不一致 | 能力树必须最后更新，与实际文件一一对应 |
| 10 | 占位符（`<module>`、`<endpoint>`、`<skill-name>`）残留在最终产物中 | 全文搜索并替换为实际值 |
| 11 | 使用了绝对路径（如 `/home/user/skill/...`） | 所有路径必须使用相对路径 |
| 12 | 向用户询问 token / 鉴权 / 登录相关问题 | 鉴权统一交给 `cms-auth-skills`，不要向用户暴露中间过程 |
| 13 | 跳过了步骤间的自检关卡 | 每个步骤完成后必须逐项自检，全部通过才进入下一步 |
| 14 | 反思时只写"全部通过"没有列出证据 | 第二轮交叉验证必须输出文件清单、绑定对照表等具体证据 |
| 15 | 不知道最终产物应该长什么样 | 对照附录 E 的完整示例，确保结构和格式一致 |

---

## 四、验证清单

Skill 包生成后，必须逐项检查以下内容：

### A. 结构与目录

- [ ] 存在 `SKILL.md`
- [ ] `SKILL.md` 包含宪章、工作流、目录树、模块索引表、能力概览
- [ ] `SKILL.md` 的 YAML 头包含 `name`、`description`、`skillcode`
- [ ] `SKILL.md` 的 YAML 头包含 `dependencies: - cms-auth-skills`
- [ ] 每个业务模块都有 `openapi/<module>/api-index.md`
- [ ] 每个业务接口都有独立文档 `openapi/<module>/<endpoint>.md`
- [ ] 每个业务接口都有对应脚本 `scripts/<module>/<endpoint>.py`
- [ ] `examples/<module>/README.md` 存在
- [ ] `scripts/<module>/README.md` 存在
- [ ] 所有脚本均为 Python（`.py`）文件

### B. 模块与目录一致性

- [ ] `SKILL.md` 能力概览中的模块名 = `openapi/` 下模块目录
- [ ] `SKILL.md` 模块索引表中的模块名 = `openapi/` 下模块目录
- [ ] `SKILL.md` 目录树 = 实际目录结构
- [ ] `api-index.md` 中列出的接口文档都存在
- [ ] `api-index.md` 中列出的脚本路径都存在
- [ ] `openapi/<module>/<endpoint>.md` 与 `scripts/<module>/<endpoint>.py` 保持 1:1 对应
- [ ] 不存在"孤立模块"或"孤立文件"

### C. 内容与一致性

- [ ] `SKILL.md` 仅作为索引（不包含完整接口参数）
- [ ] `api-index.md` 仅列接口清单与脚本映射
- [ ] 每个接口文档包含：作用、鉴权类型、Headers、参数表、Schema、脚本映射
- [ ] 每个脚本包含：API 调用、JSON 输出
- [ ] 全文不存在占位符（`<module>`、`<endpoint>`、`<skill-name>` 等）
- [ ] 全文不存在绝对路径

### D. 鉴权与安全

- [ ] 目标 `SKILL.md` 的 YAML 头已声明 `dependencies: - cms-auth-skills`
- [ ] 目标 `SKILL.md` 的 `skillcode` 与实际 Skill 标识一致
- [ ] 目标 `SKILL.md` 明确引用 `cms-auth-skills/common/auth.md` 与 `cms-auth-skills/common/conventions.md`
- [ ] 目标 `SKILL.md` 包含"授权依赖"安装指引（cms-auth-skills 的检查与安装说明，含 `npx clawhub@latest install` 命令）
- [ ] 每个业务接口文档都明确声明一个且仅一个鉴权类型：`nologin`、`appKey`、`access-token`
- [ ] 目标 Skill 未生成本地 `common/auth.md`、`common/conventions.md`、`openapi/common/appkey.md`、`scripts/auth/login.py`
- [ ] 业务请求按接口声明使用 `nologin`、`appKey` 或 `access-token`
- [ ] 需要鉴权时，明确由 `cms-auth-skills` 预先准备 `appKey` 或 `access-token`
- [ ] 不向用户泄露 token/userId/personId 等敏感字段

### E. 脚本完整性

> 以下检查仅针对 `scripts/<module>/` 下的业务脚本。

- [ ] 每个业务接口都有对应 `.py` 脚本（不允许"暂无脚本"）
- [ ] 每个需要鉴权的业务脚本，其使用说明明确依赖 `cms-auth-skills`
- [ ] 每个需要鉴权的业务脚本，按接口声明读取对应鉴权值（`appKey` → `XG_BIZ_API_KEY/XG_APP_KEY`；`access-token` → `XG_USER_TOKEN`）
- [ ] `nologin` 脚本不读取鉴权环境变量
- [ ] 业务脚本不直接调用授权接口，也不实现本地登录逻辑
- [ ] 每个业务脚本的 `API_URL` 硬写完整 URL（含域名），与对应 `endpoint.md` 一致
- [ ] 每个业务脚本有 `main()` 函数和 `if __name__ == "__main__"` 守卫
- [ ] 每个业务脚本的入参字段与对应 `endpoint.md` 参数表一致

### F. 异步、超时与重试

- [ ] 重试间隔 ≥ 1 秒、最多 3 次
- [ ] 不存在无限循环重试

### G. 危险操作

- [ ] 存在"危险操作友好拒绝"规则声明

### H. 输出规范

- [ ] 对用户输出最小必要信息：摘要/必要输入/链接
- [ ] 仅 `open-link` 可以输出带 token 的完整 URL
- [ ] 仅在必须时输出最小 ID（如 notebookId/sourceId）
- [ ] 不回显完整 JSON 响应

---

## 附录 A：目标 SKILL.md 的依赖声明

> **写入位置**：目标 `SKILL.md` 的 YAML 头
> **性质**：固定要求，所有需要统一鉴权的 Skill 都必须包含。

```yaml
dependencies:
  - cms-auth-skills
```

---

## 附录 B：统一鉴权引用规则

> **性质**：固定要求，禁止替换为本地 auth/common 文件。

- 目标 Skill 不再创建 `common/auth.md`
- 目标 Skill 不再创建 `common/conventions.md`
- 目标 Skill 不再创建 `openapi/common/appkey.md`
- 目标 Skill 不再创建 `scripts/auth/login.py`
- 目标 `SKILL.md` 中的统一规范必须引用：
  - `cms-auth-skills/common/conventions.md`
  - `cms-auth-skills/common/auth.md`
- 如需查看授权接口说明，统一引用：
  - `cms-auth-skills/openapi/auth/appkey.md`
  - `cms-auth-skills/openapi/auth/login.md`
- 每个业务接口文档都必须声明一个且仅一个鉴权类型：`nologin`、`appKey`、`access-token`
- 每个业务脚本都只读取已准备好的鉴权值，不负责获取 `appKey` / `access-token`
- 如接口需要鉴权，先由 `cms-auth-skills` 准备 `appKey` 或 `access-token`

---

## 附录 C：cms-auth-skills 安装与预检

> **性质**：固定要求，执行任何需要鉴权的业务前都应先检查。

优先安装方式：

```bash
npx clawhub@latest install cms-auth-skills --force
```

备用安装方式：

```bash
npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force
```

预检规则：

- 如果 `cms-auth-skills` 已安装，直接使用
- 如果未安装，先完成安装再执行需要鉴权的业务
- 先读取目标接口文档的"鉴权类型"，判断是 `nologin`、`appKey` 还是 `access-token`
- 如果接口是 `nologin`，直接执行业务脚本，无需准备鉴权值
- `access-token` 接口的业务脚本读取 `XG_USER_TOKEN`
- `appKey` 接口的业务脚本读取 `XG_BIZ_API_KEY` 或 `XG_APP_KEY`
- 以上鉴权值应由 `cms-auth-skills` 预先准备

---

## 附录 D：快速参考卡片

| 要创建的文件 | 格式参考 | 写入路径 | 固定/动态 |
|---|---|---|---|
| `dependencies: - cms-auth-skills` | 附录 A | `SKILL.md` YAML 头 | **固定要求** |
| 鉴权引用规则 | 附录 B | `SKILL.md` / 使用说明 | **固定要求** |
| 安装与预检规则 | 附录 C | 执行前检查 | **固定要求** |
| 鉴权类型声明 | §2.3 / 附录 B | `openapi/<module>/<endpoint>.md` | **固定要求** |
| 禁止本地登录脚本 | 本章 1.5 / 附录 B | 目录结构约束 | **固定要求** |
| `SKILL.md` | §2.1 | `SKILL.md` | **动态**，根据业务生成 |
| `api-index.md` | §2.2 | `openapi/<module>/api-index.md` | **动态**，根据接口生成 |
| `<endpoint>.md` | §2.3 | `openapi/<module>/<endpoint>.md` | **动态**，根据接口生成 |
| `README.md`（示例） | §2.4 | `examples/<module>/README.md` | **动态**，根据业务生成 |
| `README.md`（脚本） | §2.5 | `scripts/<module>/README.md` | **动态**，根据接口生成 |
| `<endpoint>.py` | §2.6 | `scripts/<module>/<endpoint>.py` | **动态**，每个接口一个 |

---

## 附录 E：完整迷你示例（1 模块 1 接口）

> **本示例是弱模型的"对照标本"**。生成完成后，将你的 Skill 包与本示例的结构逐一比对，确保格式和层级完全一致。
>
> 示例参数：Skill 名称 = `demo-weather`，模块 = `forecast`，接口 = `get-current`，生产域名 = `api.weather-demo.com`
>
> 文件计数：1（SKILL.md）+ 1×3（模块索引）+ 1×2（接口文件）= **6 个文件**

### E.1 目录结构

```
demo-weather/
├── SKILL.md
├── openapi/
│   └── forecast/
│       ├── api-index.md
│       └── get-current.md
├── examples/
│   └── forecast/
│       └── README.md
└── scripts/
    └── forecast/
        ├── README.md
        └── get-current.py
```

### E.2 SKILL.md

```markdown
---
name: demo-weather
description: 查询天气预报信息
skillcode: demo-weather
dependencies:
  - cms-auth-skills
---

# Demo-Weather — 索引

本文件提供**能力宪章 + 能力树 + 按需加载规则**。详细参数与流程见各模块 `openapi/` 与 `examples/`。

**当前版本**: v0.1

**接口版本**: 本示例接口使用 `/openapi/*` 前缀，且该接口的鉴权类型为 `access-token`。

**能力概览（1 块能力）**：
- `forecast`：查询当前天气（温度、湿度、天气状况）

统一规范：
- 认证与鉴权：`cms-auth-skills/common/auth.md`
- 通用约束：`cms-auth-skills/common/conventions.md`

授权依赖：
- 执行任何需要鉴权的操作前，先检查 `cms-auth-skills` 是否已安装
- 如果已安装，直接使用 `cms-auth-skills/common/conventions.md`、`cms-auth-skills/common/auth.md`、`cms-auth-skills/openapi/auth/appkey.md`、`cms-auth-skills/openapi/auth/login.md`
- 如果未安装，先执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续执行需要鉴权的操作

输入完整性规则（强制）：
1. 查询天气必须提供城市名称
2. 不允许同时查询超过 5 个城市

建议工作流（简版）：
1. 读取 `SKILL.md` 与 `cms-auth-skills/common/*`，明确能力范围、鉴权与安全约束。
2. 识别用户意图并路由模块，先打开 `openapi/forecast/api-index.md`。
3. 确认具体接口后，加载 `openapi/forecast/get-current.md` 获取入参/出参/Schema。
4. 补齐用户必需输入（城市名称），必要时先确认。
5. 参考 `examples/forecast/README.md` 组织话术与流程。
6. **执行对应脚本**：调用 `scripts/forecast/get-current.py` 执行接口调用，获取结果。**所有接口调用必须通过脚本执行，不允许跳过脚本直接调用 API。**

脚本使用规则（强制）：
1. **每个接口必须有对应脚本**：每个 `openapi/forecast/<endpoint>.md` 都必须有对应的 `scripts/forecast/<endpoint>.py`，不允许"暂无脚本"。
2. **脚本可独立执行**：所有 `scripts/` 下的脚本均可脱离 AI Agent 直接在命令行运行。
3. **先读文档再执行**：执行脚本前，**必须先阅读对应模块的 `openapi/forecast/api-index.md`**。
4. **入参来源**：脚本的所有入参定义与字段说明以 `openapi/` 文档为准，脚本仅负责编排调用流程。
5. **鉴权一致**：脚本内部同样遵循 `cms-auth-skills/common/auth.md` 的鉴权规则。

意图路由与加载规则（强制）：
1. **先路由再加载**：必须先判定模块，再打开该模块的 `api-index.md`。
2. **先读文档再调用**：在描述调用或执行前，必须加载对应接口文档。
3. **脚本必须执行**：所有接口调用必须通过脚本执行，不允许跳过。
4. **不猜测**：若意图不明确，必须追问澄清。

宪章（必须遵守）：
1. **只读索引**：`SKILL.md` 只描述"能做什么"和"去哪里读"，不写具体接口参数。
2. **按需加载**：默认只读 `SKILL.md` + `cms-auth-skills/common/*`，只有触发某模块时才加载该模块的 `openapi`、`examples` 与 `scripts`。
3. **对外克制**：对用户只输出"可用能力、必要输入、结果链接或摘要"，不暴露鉴权细节与内部字段。
4. **素材优先级**：用户给了文件或 URL，必须先提取内容再确认，确认后才触发生成或写入。
5. **生产约束**：仅允许生产域名与生产协议，不引入任何测试地址。
6. **接口拆分**：每个 API 独立成文档；模块内 `api-index.md` 仅做索引。
7. **危险操作**：对可能导致数据泄露、破坏、越权的请求，应礼貌拒绝并给出安全替代方案。
8. **脚本语言限制**：所有脚本**必须使用 Python 编写**。
9. **重试策略**：出错时**间隔 1 秒、最多重试 3 次**，超过后终止并上报。
10. **禁止无限重试**：严禁无限循环重试。

模块路由与能力索引（合并版）：

| 用户意图（示例） | 模块 | 能力摘要 | 接口文档 | 示例模板 | 脚本 |
|---|---|---|---|---|---|
| "帮我查一下北京的天气" | `forecast` | 查询当前天气 | `./openapi/forecast/api-index.md` | `./examples/forecast/README.md` | `./scripts/forecast/get-current.py` |

能力树（实际目录结构）：
\```text
demo-weather/
├── SKILL.md
├── openapi/
│   └── forecast/
│       ├── api-index.md
│       └── get-current.md
├── examples/
│   └── forecast/README.md
└── scripts/
    └── forecast/
        ├── README.md
        └── get-current.py
\```
```

### E.3 openapi/forecast/api-index.md

```markdown
# API 索引 — forecast

接口列表：

1. `GET /openapi/weather/current`
   - 文档：`./get-current.md`

脚本映射：
- `../../scripts/forecast/README.md`
```

### E.4 openapi/forecast/get-current.md

```markdown
# GET https://api.weather-demo.com/openapi/weather/current

## 作用

查询指定城市的当前天气信息，返回温度、湿度和天气状况。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `city` | string | 是 | 城市名称（如"北京"） |

## 请求 Schema
\```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["city"],
  "properties": {
    "city": { "type": "string", "description": "城市名称" }
  }
}
\```

## 响应 Schema
\```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "data": {
      "type": "object",
      "properties": {
        "city": { "type": "string" },
        "temperature": { "type": "number" },
        "humidity": { "type": "number" },
        "condition": { "type": "string" }
      }
    }
  }
}
\```

## 脚本映射

- `../../scripts/forecast/get-current.py`
```

### E.5 examples/forecast/README.md

```markdown
# forecast — 使用说明

## 什么时候使用

- 用户问"今天天气怎么样"、"北京天气如何"、"查一下上海的温度"
- 需要获取某个城市的实时天气数据时

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 确认用户要查询的城市名称
3. 调用 `scripts/forecast/get-current.py` 执行查询
4. 输出天气摘要（城市、温度、湿度、天气状况）
```

### E.6 scripts/forecast/README.md

```markdown
# 脚本清单 — forecast

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-current.py` | `GET /openapi/weather/current` | 查询当前天气，输出 JSON 结果 |

## 使用方式

\```bash
# 先通过 cms-auth-skills 准备 access-token，再设置环境变量
export XG_USER_TOKEN="your-access-token"

# 执行脚本
python3 scripts/forecast/get-current.py
\```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **入参定义以** `openapi/` 文档为准
```

### E.7 scripts/forecast/get-current.py

```python
#!/usr/bin/env python3
"""
forecast / get-current 脚本

用途：查询指定城市的当前天气信息

使用方式：
  python3 scripts/forecast/get-current.py

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/forecast/get-current.md 中声明的一致）
API_URL = "https://api.weather-demo.com/openapi/weather/current"
AUTH_MODE = "access-token"

def build_headers() -> dict:
    """根据鉴权模式构造请求头"""
    token = os.environ.get("XG_USER_TOKEN")

    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)

    return {
        "access-token": token,
        "Content-Type": "application/json",
    }


def call_api(city: str) -> dict:
    """调用天气查询接口，返回原始 JSON 响应"""
    headers = build_headers()

    # Query 参数拼接到 URL
    url = f"{API_URL}?city={urllib.parse.quote(city)}"

    req = urllib.request.Request(url, headers=headers, method="GET")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    # 从命令行参数获取城市名（默认"北京"）
    city = sys.argv[1] if len(sys.argv) > 1 else "北京"

    # 1. 调用接口，获取原始 JSON
    result = call_api(city)

    # 2. 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

> **注意**：以上示例中，目标 Skill 不再创建本地 `common/`、`openapi/common/` 或 `scripts/auth/` 授权文件；统一依赖 `cms-auth-skills` 提供鉴权规则、授权接口说明与登录能力。
