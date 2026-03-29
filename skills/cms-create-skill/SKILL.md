---
name: cms-create-skill
description: CMS Skill 创建工具 — 三位一体的 Skill 全生命周期工具：发现平台已有 Skill、按 XGJK 协议创建新 Skill、发布/更新/下架 Skill
skillcode: cms-create-skill
dependencies:
  - cms-auth-skills
---

# CMS Skill 创建工具

**当前版本**: v1.0.7

> **⚠️ 身份声明**：本 Skill 是 **Skill 全生命周期工具**，提供三大核心能力：
>
> ## 三大核心能力
>
> | # | 核心能力 | 说明 | 是否需要登录 |
> |---|---------|------|------------|
> | 🔍 | **发现 Skill** | 浏览平台已有 Skill、查看详情、搜索筛选 | 否 |
> | 🛠️ | **创建 Skill** | 按 XGJK 协议模板，多轮对话引导从零构建完整 Skill 包 | 否 |
> | 🚀 | **发布 Skill** | 打包 → 上传 → 注册/更新/下架，完整生命周期管理 | 是 |
>
> **命名区分**：
> - "发现 Skill" = 调用查询接口，浏览和了解平台现有 Skill（**入口，先看有什么**）
> - "创建 Skill" = 使用本工具的 **生成流程**（Step 1-5）来按协议模板创建一套新的 Skill 文件
> - "发布 Skill" = 调用 **skill-management 模块**的接口，将已完成的 Skill 注册到平台

---

## 能力宪章

### 核心原则（铁律）

1. **禁止问用户任何关于 token / 鉴权 / 登录的问题** — 鉴权统一依赖 `cms-auth-skills`
2. **只有需要鉴权的操作才获取 token** — `get-skills`（nologin 接口）和创建流程（Step 1-5）不需要 token
3. **每一步都要跟用户确认** — 不自作主张，不跳步
4. **5 步创建流程不可跳过** — 必须严格按 Step 1 → 2 → 3 → 4 → 5 顺序执行
5. **生成的 Skill 必须严格遵循** `docs/XGJK_SKILL_PROTOCOL.md`
6. **鉴权依赖必须统一** — 目标 Skill 不再生成本地 auth/common，统一依赖 `cms-auth-skills`
7. **生成出的目标 Skill 必须声明依赖** — 目标 `SKILL.md` 的 YAML 头必须包含 `dependencies: - cms-auth-skills`

### 鉴权规则

- **需要 token 的操作**：`register-skill`、`update-skill`、`delete-skill`
- **不需要 token 的操作**：`get-skills`（nologin 接口）、Skill 包生成流程（Step 1-5）、`fetch_api_doc.py`
- 鉴权流程详见 `cms-auth-skills/common/auth.md`

### 授权依赖

- 执行任何需要鉴权的操作前，先检查 `cms-auth-skills` 是否已安装
- 如果已安装，直接使用 `cms-auth-skills/common/conventions.md`、`cms-auth-skills/common/auth.md`、`cms-auth-skills/openapi/auth/appkey.md`、`cms-auth-skills/openapi/auth/login.md`
- 如果未安装，先执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续发布、更新、下架等需要鉴权的操作

---

## 能力概览

### 🔍 发现 Skill（Discover）

| 能力 | 模块 | 说明 | 需要登录 |
|---|---|---|---|
| 打开技能管理平台 | — | 在浏览器打开 https://skills.mediportal.com.cn | 否 |
| 浏览 Skill 列表 | `skill-management` | 查看平台所有已发布 Skill，含名称、描述、版本、状态 | 否 |
| 搜索 Skill | `skill-management` | 按关键词搜索 Skill（名称/描述模糊匹配） | 否 |
| 查看 Skill 详情 | `skill-management` | 查看某个 Skill 的完整信息（含下载地址、版本历史等） | 否 |

### 🛠️ 创建 Skill（Create）

| 能力 | 模块 | 说明 | 需要登录 |
|---|---|---|---|
| 按协议构建 Skill 包 | 生成流程 Step 1-5 | 多轮对话引导，按 XGJK 协议模板从零生成完整 Skill 包，并在目标 `SKILL.md` 中声明依赖 `cms-auth-skills` | 否 |
| 获取接口文档 | 工具脚本 | 自动识别 Swagger / Markdown URL，拉取并解析接口定义 | 否 |

### 🚀 发布 Skill（Publish）

| 能力 | 模块 | 说明 | 需要登录 |
|---|---|---|---|
| 一站式发布 | `skill-management` | 打包 + 上传七牛 + 注册，一条命令完成 | 是 |
| 打包 Skill 为 ZIP | `skill-management` | 将 Skill 目录打成 .zip 文件 | 否 |
| 上传到七牛 | `skill-management` | 获取七牛凭证 + 上传 ZIP，返回下载地址 | 是 |
| 发布（注册）Skill | `skill-management` | 将 Skill 包注册到平台 | 是 |
| 更新已有 Skill | `skill-management` | 修改已发布 Skill 的名称、描述、版本等信息 | 是 |
| 下架 Skill | `skill-management` | 从平台移除一个已发布的 Skill | 是 |

---

## 意图路由表

### 🔍 发现 Skill

| 用户说 | 路由到 | 打开文档 | 执行脚本 | 需要 token |
|---|---|---|---|---|
| "打开技能管理"/"打开玄关Skill"/"Skill管理页面" | 浏览器打开 | — | `open https://skills.mediportal.com.cn` 或返回链接 | 否 |
| "有哪些 Skill"/"查看 Skill 列表"/"看看都有什么" | skill-management | `openapi/skill-management/get-skills.md` | `scripts/skill-management/get_skills.py` | 否 |
| "搜索 xxx Skill"/"找一下 xxx 相关的" | skill-management | `openapi/skill-management/get-skills.md` | `scripts/skill-management/get_skills.py --search xxx` | 否 |
| "xxx 这个 Skill 怎么样"/"看看 xxx 的详情" | skill-management | `openapi/skill-management/get-skills.md` | `scripts/skill-management/get_skills.py --detail xxx` | 否 |

### 🛠️ 创建 Skill

| 用户说 | 路由到 | 打开文档 | 执行脚本 | 需要 token |
|---|---|---|---|---|
| "构建 Skill 包"/"按模板创建 Skill" | **生成流程** Step 1-5 | `docs/SKILL_CREATION_WORKFLOW.md` | `scripts/fetch_api_doc.py` | 否 |
| "获取接口文档"/"拉取 API 定义" | 工具脚本 | — | `scripts/fetch_api_doc.py` | 否 |

### 🚀 发布 Skill

| 用户说 | 路由到 | 打开文档 | 执行脚本 | 需要 token |
|---|---|---|---|---|
| "打包并发布"/"帮我发布这个 Skill" | skill-management | `openapi/skill-management/publish-skill.md` | `scripts/skill-management/publish_skill.py` | 是 |
| "打包并更新"/"更新这个 Skill" | skill-management | `openapi/skill-management/publish-skill.md` | `scripts/skill-management/publish_skill.py --update` | 是 |
| "打包 Skill"/"生成 ZIP" | skill-management | `openapi/skill-management/pack-skill.md` | `scripts/skill-management/pack_skill.py` | 否 |
| "上传到七牛"/"上传 ZIP" | skill-management | `openapi/skill-management/upload-to-qiniu.md` | `scripts/skill-management/upload_to_qiniu.py` | 是 |
| "发布 Skill"/"注册 Skill" | skill-management | `openapi/skill-management/register-skill.md` | `scripts/skill-management/register_skill.py` | 是 |
| "更新 Skill"/"修改 Skill 信息" | skill-management | `openapi/skill-management/update-skill.md` | `scripts/skill-management/update_skill.py` | 是 |
| "下架 Skill"/"删除 Skill" | skill-management | `openapi/skill-management/delete-skill.md` | `scripts/skill-management/delete_skill.py` | 是 |

---

## 工作流 A：🔍 发现 Skill

> 发现是起点 — 先看看平台上有什么，再决定是否要创建新的。

### 打开技能管理平台（网页）

用户说"打开玄关的技能管理"、"打开 Skill 管理页面"时，**两种方式都支持**：

1. **浏览器直接打开**（优先，如有 MCP 浏览器工具可用）：
```bash
open https://skills.mediportal.com.cn
```

2. **返回链接给用户**：
> 玄关技能管理平台：https://skills.mediportal.com.cn

### 命令行查询

```bash
# 浏览全部 Skill（无需 token）
python3 cms-create-skill/scripts/skill-management/get_skills.py

# 按关键词搜索
python3 cms-create-skill/scripts/skill-management/get_skills.py --search "机器人"

# 查看某个 Skill 详情
python3 cms-create-skill/scripts/skill-management/get_skills.py --detail "im-robot"
```

**输出格式**：
- 列表模式：表格展示 `名称 | 描述 | 版本 | 状态 | 更新时间`
- 详情模式：展示完整信息 + 下载地址
- 搜索模式：名称和描述模糊匹配

---

## 工作流 B：🛠️ 创建 Skill（5 步流程）

> **完整操作手册**：`docs/SKILL_CREATION_WORKFLOW.md`
> **协议规范**：`docs/XGJK_SKILL_PROTOCOL.md`
> **验证清单**：`docs/SKILL_VALIDATION_CHECKLIST.md`

```
Step 1  意图理解与需求确认 → 了解场景、获取文档、筛选 API、精简字段
Step 2  按协议逐步生成    → 搭骨架、约定鉴权依赖、生成 SKILL.md、逐个 API 生成、写索引
Step 3  三轮反思检查       → 验证清单 A-H → 交叉验证（附证据） → 与示例结构比对
Step 4  最终确认           → 确认所有修复项清零
Step 5  完成输出总结
```

**关键约束**：
- 5 步顺序执行，不可跳过
- 每步都有自检关卡，必须全部通过才能进入下一步
- 不需要登录 token

---

## 工作流 C：🚀 发布 Skill

> 使用 `skill-management` 模块管理 Skill 的完整生命周期。接口详情见 `openapi/skill-management/` 目录。

### 一站式发布（推荐）

```bash
# 首次发布（打包 + 上传七牛 + 注册，一条命令）
python3 cms-create-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人"

# 更新已有 Skill（打包 + 上传七牛 + 更新，一条命令）
python3 cms-create-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --update --version 2
```

> `publish_skill.py` 自动串联：打包 ZIP → 获取七牛凭证 → 上传 → 注册/更新。执行前先通过 `cms-auth-skills` 准备好 `access-token`，并写入 `XG_USER_TOKEN`。

### 分步操作 / 其他管理

```bash
# 仅打包（无需 token）
python3 cms-create-skill/scripts/skill-management/pack_skill.py ./im-robot

# 仅上传（需要先通过 cms-auth-skills 准备 XG_USER_TOKEN）
python3 cms-create-skill/scripts/skill-management/upload_to_qiniu.py ./im-robot.zip

# 下架 Skill（需要先通过 cms-auth-skills 准备 XG_USER_TOKEN）
python3 cms-create-skill/scripts/skill-management/delete_skill.py --id <skill-id> [--reason <原因>]
```

---

## 约束

1. **5 步顺序执行**：Step 1 → 2 → 3 → 4 → 5，不跳步
2. **多轮对话**：每一步都要跟用户确认，不自作主张
3. **协议规范**：生成的 Skill 包必须严格遵循 `docs/XGJK_SKILL_PROTOCOL.md`
4. **目标 Skill 必须声明依赖**：目标 `SKILL.md` 的 YAML 头必须包含 `dependencies: - cms-auth-skills`
5. **鉴权依赖不可偏离**：目标 Skill 不创建本地 auth/common，统一依赖 `cms-auth-skills`
6. **禁止问鉴权问题**：不要问用户关于 token、登录、鉴权的任何问题
7. **脚本必须生成**：每个接口都必须有对应的 Python 脚本
8. **逐个 API 生成**：Step 2.3 一个 API 写完全套（文档 + 脚本 + 场景）再进下一个
9. **反思检查不可跳过**：Step 3（三轮反思）和 Step 4（最终确认）必须完整执行
10. **重试策略**：脚本执行出错时，间隔 1 秒、最多重试 3 次，禁止无限重试
11. **生产域名**：生成前确认生产域名，未提供则在 API_URL 中用 `{待确认域名}` 占位并提醒用户
12. **按需鉴权**：nologin 接口不需要 token，创建流程不需要 token，仅写操作（注册/更新/下架）需要

## 能力树

```
cms-create-skill/                            # CMS Skill 创建工具
├── SKILL.md                                 # 本文件（技能定义）
├── docs/
│   ├── XGJK_SKILL_PROTOCOL.md              #   [创建] 协议规范（自包含）
│   ├── SKILL_CREATION_WORKFLOW.md           #   [创建] 5 步构建流程操作手册
│   └── SKILL_VALIDATION_CHECKLIST.md        #   [创建] 验证清单（Step 3 逐项检查用）
├── openapi/
│   └── skill-management/                    #   模块：Skill 生命周期管理
│       ├── api-index.md                     #     接口索引
│       ├── get-skills.md                    #     [发现] 浏览/搜索/详情（nologin）
│       ├── publish-skill.md                 #     [发布] 一站式发布（打包→上传→注册/更新）
│       ├── pack-skill.md                    #     [发布] 打包 Skill 为 ZIP
│       ├── upload-to-qiniu.md               #     [发布] 上传到七牛（需要 auth）
│       ├── register-skill.md                #     [发布] 注册新 Skill（需要 auth）
│       ├── update-skill.md                  #     [发布] 更新 Skill（需要 auth）
│       └── delete-skill.md                  #     [发布] 下架 Skill（需要 auth）
├── examples/
│   └── skill-management/
│       └── README.md                        #   使用场景与触发条件
└── scripts/
    ├── fetch_api_doc.py                     #   [创建] 接口文档获取器（Swagger/Markdown）
    └── skill-management/                    #   模块：Skill 生命周期管理
        ├── README.md                        #     脚本清单 + 使用示例
        ├── get_skills.py                    #     [发现] 浏览/搜索/详情（--search/--detail）
        ├── publish_skill.py                 #     [发布] 一站式发布（打包→上传→注册/更新）
        ├── pack_skill.py                    #     [发布] 打包 Skill 为 ZIP（无需 token）
        ├── upload_to_qiniu.py               #     [发布] 上传到七牛 
        ├── register_skill.py                #     [发布] 注册新 Skill 
        ├── update_skill.py                  #     [发布] 更新 Skill 
        └── delete_skill.py                  #     [发布] 下架 Skill 
```

## 备注

- `docs/XGJK_SKILL_PROTOCOL.md` 是一份**自包含的协议规范**，可以独立交给任意 AI 使用，无需本 Skill 参与。
- 本 Skill 自身的 `openapi/`、`scripts/` 结构遵循 XGJK 协议；登录授权统一由 `cms-auth-skills` 提供。
- 本 Skill 的 **生成流程**（Step 1-5）是 Meta-Skill 能力，协议的验证标尺仅适用于生成的 Skill 包。
