---
name: notex-skills
description: NoteX 技能路由网关索引（access-token 鉴权，由 cms-auth-skills 统一提供），覆盖内容生产（PPT/视频/音频/报告/脑图/测验/闪卡/信息图）、运营数据问答与洞察、笔记本管理（列表/统计/创建/追加来源）、来源索引与详情定位、首页登录链接生成。
dependencies:
  - cms-auth-skills
---

# NoteX Skills — 索引

本文件提供**能力宪章 + 能力树 + 按需加载规则**。详细参数与流程见各模块 `openapi/` 与 `examples/`。

**当前版本**: v1.3

**接口版本**: 所有业务接口统一使用 `/openapi/*` 前缀，自带 `access-token` 鉴权，不依赖网关。

**能力概览（5 块能力）**：
- `open-link`：生成带 token 的 NoteX 首页访问链接
- `creator`：内容生产（八个工作室模块：PPT/视频/音频/报告/脑图/测验/闪卡/信息图）
- `ops`：运营数据问答与洞察
- `notebooks`：笔记本列表/统计/创建/追加来源
- `sources`：来源索引树与最小详情定位

统一规范：
- 认证与鉴权：统一由 `cms-auth-skills` 提供，详见 `cms-auth-skills/SKILL.md`

### 鉴权模式声明（重要）

> **NoteX 所有业务接口仅支持 `access-token` 鉴权模式，不支持 `appKey` 直接鉴权。**
>
> - 对应 `cms-auth-skills` 的 `login.py`，NoteX 场景**只允许使用 `--ensure` 参数**（返回 `access-token`）
> - **禁止使用 `--resolve-app-key`**（只返回 appKey，NoteX 接口无法识别）
> - **禁止使用 `--headers --auth-mode appKey`**（会构造 `appKey` Header，NoteX 接口不接受）
> - 正确用法：`python3 login.py --ensure` → 返回可直接用于 `access-token` Header 的 token 值
> - 内部流程：`login.py --ensure` 会自动完成 `appKey 获取 → 换取 access-token` 的全链路，调用方无需关心中间步骤

### 鉴权宪章（铁律）

1. **禁止问用户任何关于 token / 鉴权 / 登录的问题** — 鉴权统一依赖 `cms-auth-skills`
2. **所有鉴权操作必须且只能通过 `cms-auth-skills/scripts/auth/login.py --ensure` 执行**，严禁在脚本中直接调用底层 HTTP 鉴权接口
3. **鉴权模式锁定**：NoteX 所有接口只接受 `access-token`，不接受 `appKey`；调用 `login.py` 时**必须用 `--ensure`**
4. **对外克制**：对用户只输出"可用能力、必要输入、结果链接或摘要"，不暴露鉴权细节与内部字段

### 授权依赖

- 当需要 `access-token` 时，优先直接读取 `cms-auth-skills/SKILL.md`
- 如果能读取到，直接按 `cms-auth-skills/SKILL.md` 中的鉴权规则，使用 `login.py --ensure` 准备 `access-token`
- 如果读取不到（说明未安装），再执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续需要鉴权的操作

输入完整性规则（强制）：
1. **内容生产必须完整**：调用 `creator` 的八个工作室模块时，必须提供完整上下文文本（`context_text`），不接受摘要、截断或缺失段落的内容。
2. **追加来源必须完整**：`notebooks/add-source` 的来源内容必须是完整原文，避免只传摘要或片段。

素材解析与技能建议（场景补充）：
- 若用户丢链接/文件并要求生成 PPT/音频概览/报告等，建议先使用对应的**解析类技能**提取完整正文，再将完整内容传入 `creator` 的任务请求。

建议工作流（简版）：
1. 读取 `SKILL.md`，明确能力范围与鉴权依赖（`cms-auth-skills`）。
2. 识别用户意图并路由模块，先打开 `openapi/<module>/api-index.md`。
3. 确认具体接口后，加载 `openapi/<module>/<endpoint>.md` 获取入参/出参/Schema。
4. 补齐用户必需输入，必要时先读取用户文件/URL 并确认摘要。
5. 参考 `examples/<module>/README.md` 组织话术与流程。
6. 若需要联调、批量或复杂编排，再加载对应 `scripts/`。

脚本使用规则（强制）：
1. **脚本可独立执行**：所有 `scripts/` 下的脚本均可脱离 AI Agent 直接在命令行运行。
2. **先读文档再执行**：执行脚本前，**必须先阅读对应模块的 `openapi/<module>/api-index.md`**，获取完整入参说明与约束条件。
3. **入参来源**：脚本的所有入参定义与字段说明以 `openapi/` 文档为准，脚本仅负责编排调用流程。
4. **鉴权一致**：脚本内部统一通过 `cms-auth-skills/scripts/auth/login.py` 获取鉴权值（环境变量 `XG_USER_TOKEN` → `login.py --ensure`）。
5. **零依赖**：脚本仅使用 Python 标准库。
6. **stdout = 结果，stderr = 日志**。

意图路由与加载规则（强制）：
1. **先路由再加载**：必须先判定模块，再打开该模块的 `api-index.md`。
2. **先读文档再调用**：在描述调用或执行前，必须加载对应接口文档（`openapi/<module>/<endpoint>.md`）。
3. **脚本按需**：涉及联调、批量或复杂编排时，必须加载对应 `scripts/`。
4. **不猜测**：若意图不明确，必须追问澄清，不允许跨模块或"默认模块"猜测。

宪章（必须遵守）：
1. **只读索引**：`SKILL.md` 只描述"能做什么"和"去哪里读"，不写具体接口参数。
2. **按需加载**：默认只读 `SKILL.md`，只有触发某模块时才加载该模块的 `openapi` 与 `examples`，必要时再加载 `scripts`。
3. **对外克制**：对用户只输出"可用能力、必要输入、结果链接或摘要"，不暴露鉴权细节与内部字段。
4. **素材优先级**：用户给了文件或 URL，必须先提取内容再确认，确认后才触发生成或写入。
5. **生产约束**：仅允许生产域名与生产协议，不引入任何测试地址。
6. **接口拆分**：每个 API 独立成文档，路径为 `openapi/<module>/<endpoint>.md`；模块内 `api-index.md` 仅做索引。
7. **危险操作**：对可能导致数据泄露、破坏、越权或高风险副作用的请求，应礼貌拒绝并给出安全替代方案。

通用约束与约定：
1. **Header 规范**：所有业务接口统一携带 `access-token`（必传）、`Content-Type: application/json`（POST）。
2. **输出与脱敏**：对用户输出结论/摘要/可访问链接/必要操作提示。默认不输出 `token/xgToken/access-token`、`appKey/CWork Key`（除非索取授权）、任何内部主键。仅 `open-link` 场景允许返回带 token 的完整 URL。
3. **输入与请求校验**：所有接口参数需做类型/长度/枚举校验。文件与 URL 输入需限制类型、大小、超时与重定向。
4. **JSON 与字段回显**：不回显完整 JSON 响应。仅提取必要字段，避免输出过长列表或敏感字段。
5. **外部能力与数据来源**：使用文件或 URL 作为来源时，先读取并摘要确认，再触发生成或写入。不编造数据。
6. **轮询、异步与超时**：创作类任务 60 秒轮询一次，最多 20 次；仅在完成/失败/超时时回复。ops-chat 单次请求超时上限 300000ms。其他请求默认超时 60000ms。
7. **日志与审计**：日志中不得出现 token/密钥/敏感字段。
8. **危险操作处理**：对可能导致数据泄露、破坏、越权或高风险副作用的请求，必须礼貌拒绝。
9. **重试策略**：脚本执行出错时，间隔 1 秒、最多重试 3 次，禁止无限重试。

模块路由与能力索引（合并版）：

| 用户意图（示例） | 模块 | 能力摘要 | 接口文档 | 示例模板 | 脚本（可独立执行） |
|---|---|---|---|---|---|
| 打开首页、生成登录/访问链接 | `open-link` | 生成带 token 的 NoteX 首页链接 | `./openapi/open-link/api-index.md`（`home-link.md`） | `./examples/open-link/README.md` | `./scripts/open-link/notex_open_link.py` |
| 内容生产（PPT/视频/音频/报告/脑图/测验/闪卡/信息图） | `creator` | 内容创作产物：PPT/视频/音频/报告/脑图/测验/闪卡/信息图 | `./openapi/creator/api-index.md`（`autoTask.md`、`taskStatus.md`） | `./examples/creator/README.md` | `./scripts/creator/skills_run.py` |
| 运营数据问答/洞察 | `ops` | 运营数据问答与洞察（ops-chat） | `./openapi/ops/api-index.md`（`ai-chat.md`） | `./examples/ops/README.md` | `./scripts/creator/skills_run.py`（复用） |
| 笔记本列表/统计/创建/追加来源/来源读取 | `notebooks` | 笔记本统计、列表、创建、追加来源与来源读取 | `./openapi/notebooks/api-index.md`（`list.md`、`category-counts.md`、`create.md`、`add-source.md`、`sources-list.md`、`source-content.md`） | `./examples/notebooks/README.md` | `./scripts/notebooks/notebooks_write.py`、`./scripts/notebooks/notebooks_read.py` |
| 来源索引树/详情 | `sources` | 来源索引树与最小详情定位 | `./openapi/sources/api-index.md`（`index-tree.md`、`details.md`） | `./examples/sources/README.md` | `./scripts/sources/source_index_sync.py` |

能力树（实际目录结构）：
```text
notex-skills/
├── SKILL.md
├── openapi
│   ├── creator
│   │   ├── api-index.md
│   │   ├── autoTask.md
│   │   └── taskStatus.md
│   ├── ops
│   │   ├── api-index.md
│   │   └── ai-chat.md
│   ├── notebooks
│   │   ├── api-index.md
│   │   ├── category-counts.md
│   │   ├── list.md
│   │   ├── create.md
│   │   ├── add-source.md
│   │   ├── sources-list.md
│   │   └── source-content.md
│   ├── sources
│   │   ├── api-index.md
│   │   ├── index-tree.md
│   │   └── details.md
│   └── open-link
│       ├── api-index.md
│       └── home-link.md
├── examples
│   ├── creator/README.md
│   ├── ops/README.md
│   ├── notebooks/README.md
│   ├── sources/README.md
│   └── open-link/README.md
└── scripts                          ← 所有脚本可独立执行（Python）
    ├── creator/skills_run.py        ← 执行前先读 openapi/creator/api-index.md
    ├── notebooks/notebooks_write.py ← 执行前先读 openapi/notebooks/api-index.md
    ├── notebooks/notebooks_read.py  ← 执行前先读 openapi/notebooks/api-index.md
    ├── sources/source_index_sync.py ← 执行前先读 openapi/sources/api-index.md
    ├── open-link/notex_open_link.py ← 执行前先读 openapi/open-link/api-index.md
    └── ops/                         ← 目录保留；ops-chat 复用 creator/skills_run.py
```
