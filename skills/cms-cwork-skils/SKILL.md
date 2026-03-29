---
name: cms-cwork-skils
description: CWork 工作协同原子能力集，覆盖员工搜索、文件上传下载、发送/回复汇报、收发件箱、汇报详情、任务、待办、事项、插件聚合、新消息、已读状态与 AI 问答；适用于“汇报、待办、任务、附件、消息、已读、员工查询”等场景；仅支持 appKey 鉴权并按需加载接口执行组合调用。
skillcode: cms-cwork-skils
dependencies:
  - cms-auth-skills
---

# cms-cwork-skils — 索引

本技能包基于 XGJK v1.05 协议构建，围绕《工作协同业务说明.md》《工作协同API说明.md》《基础服务业务说明.md》《基础服务-API说明.md》整理当前已覆盖的 CWork 常用协同能力，通过"一接口一脚本"的模式提供自动化办公支持。

**当前版本**: v1.3
**接口版本**: 所有业务接口统一使用 `/open-api/*` 前缀，自带 `appKey` 鉴权。

## 触发场景（用于 AI 路由）
- **高频意图**: 发汇报、回汇报、查收件箱/发件箱、查汇报详情、查待办、完成待办、建任务、查事项、查新消息、标记已读、上传附件、查员工。
- **关键词**: `工作协同` `汇报` `回复` `待办` `任务` `附件` `消息` `已读` `员工搜索` `组织架构` `AI问答`。
- **路由边界**: 仅处理 CWork 协同与基础服务接口；不做登录换 token，鉴权统一依赖 `cms-auth-skills` 提供 `appKey`。

## 能力概览
- **user-search**: 按姓名模糊搜索内部员工
- **employee-service**: 批量员工信息与组织架构信息查询
- **file-service**: 文件上传与下载信息查询
- **report-write**: 发送汇报与回复汇报
- **inbox**: 获取收件箱汇报列表
- **outbox**: 获取发件箱汇报列表
- **report-detail**: 获取单篇汇报的结构化详情
- **tasks**: 工作任务分页与任务简易信息查询
- **todos**: 待办事项管理（列表、创建的反馈、完成状态切换）
- **templates**: 最近处理事项清单与事项批量详情
- **plugin-report**: 插件场景的待办/未读聚合查询
- **report-query**: 汇报待办、汇报未读与已读判断
- **report-message**: 我的新消息与阅读汇报状态变更
- **ai-qa**: 汇报内容 AI SSE 问答
- **plan-create**: 创建高级工作任务

当前覆盖范围说明：
- 已覆盖《工作协同API说明.md》中的 24 个接口点，以及《基础服务-API说明.md》中的 5 个接口点
- 已覆盖员工搜索、批量员工信息、组织架构、文件上传、文件下载信息、发送汇报、汇报回复、收件箱/发件箱、汇报详情、任务分页、任务简易信息、通用待办、创建的反馈待办、事项列表、事项批量详情、插件聚合列表、汇报待办/未读列表、已读判断、新消息、阅读汇报、汇报 AI 问答、高级任务创建

统一规范：
- 认证与鉴权：统一由 `cms-auth-skills` 提供，详见 `cms-auth-skills/SKILL.md`

### 鉴权模式声明（重要）

> **xgjk-cwork 所有业务接口仅支持 `appKey` 鉴权模式，不支持 `access-token`。**
>
> - 对应 `cms-auth-skills` 的 `login.py`，xgjk-cwork 场景**只允许使用 `--resolve-app-key` 参数**（返回 `appKey`）
> - **禁止使用 `--ensure`**（会返回 access-token，xgjk-cwork 接口无法识别）
> - 正确用法：`python3 login.py --resolve-app-key` → 返回可直接用于 `appKey` Header 的值

### 鉴权宪章（铁律）

1. **禁止问用户任何关于 token / 鉴权 / 登录的问题** — 鉴权统一依赖 `cms-auth-skills`
2. **所有鉴权操作必须且只能通过 `cms-auth-skills/scripts/auth/login.py --resolve-app-key` 执行**，严禁在脚本中直接调用底层 HTTP 鉴权接口
3. **对外克制**：对用户只输出结论或摘要，不暴露鉴权细节与内部字段

### 授权依赖

- 当需要 `appKey` 时，优先直接读取 `cms-auth-skills/SKILL.md`
- 如果能读取到，直接按 `cms-auth-skills/SKILL.md` 中的鉴权规则，使用 `login.py --resolve-app-key` 准备 `appKey`
- 如果读取不到（说明未安装），再执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再尝试执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续后续操作

## 脚本使用规则
1. **Python 强制性**: 所有脚本必须使用 Python 编写。
2. **独立执行**: 脚本通过环境变量 `XG_BIZ_API_KEY` / `XG_APP_KEY` 运行；若本地尚未准备 `appKey`，需先按 `cms-auth-skills` 规则解析后再执行。
3. **1:1 映射**: 每个接口文档 (`openapi/`) 必须对应一个 Python 脚本 (`scripts/`)。
4. **可探测性**: 所有脚本必须支持在未设置 `appKey` 时执行 `-h/--help`，便于 AI 先探测参数再组合调用。
5. **参数策略**: 组合调用时优先使用显式参数名（如 `--report-id`、`--employee-id`、`--corp-id`），仅在兼容场景下使用位置参数。

## AI 组合调用约束（推荐）
1. **执行顺序**: 先读取 `openapi/<module>/api-index.md` 确认接口，再读取对应 `scripts/<module>/README.md` 确认参数，最后执行脚本。
2. **写操作确认**: 涉及数据变更的接口（如 `report-write/*`、`todos/complete.py`、`report-message/read-report.py`、`plan-create/create-simple.py`）必须先做明确确认再调用。
3. **大结果控制**: 对高体量接口优先使用 `--client-limit` 和 `--output-file`，默认建议只处理前 `200` 条，最大不超过 `500` 条。
4. **分页认知**: `reportInfoOpenQuery/unreadList` 实测可能忽略传入 `pageSize`，不要把脚本裁剪结果误判为平台真实分页结果。
5. **输出契约**: 所有脚本都返回 JSON；优先按 `resultCode / resultMsg / data` 读取，必要时再解析模块特定字段。

## 按需加载原则（重要）
1. **禁止全量预加载**: 不需要、也不应一次性加载全部 `27` 个接口文档与脚本说明。
2. **按任务最小读取**: 仅按当前用户意图读取最小必要集合，优先模块级索引，再下钻单接口文档与单脚本说明。
3. **分阶段扩展**: 当需求变化时再增量读取下一个模块，避免提前加载无关接口。
4. **组合调用路径**: `SKILL.md`（能力定位）→ `openapi/<module>/api-index.md`（接口候选）→ 单接口 `openapi` 文档（请求契约）→ `scripts/<module>/README.md`（参数规范）→ 单脚本执行。
5. **跨模块最小闭环**: 仅在业务链路确实需要时才跨模块组合，例如“附件汇报链路”只需 `file-service` + `report-write`，不应额外加载 `tasks/todos/plugin-report`。

## 能力树

```
cms-cwork-skils/
├── SKILL.md
├── openapi/
│   ├── user-search/
│   │   ├── api-index.md
│   │   └── search-emp.md
│   ├── employee-service/
│   │   ├── api-index.md
│   │   ├── get-by-person-ids.md
│   │   └── get-org-info.md
│   ├── file-service/
│   │   ├── api-index.md
│   │   ├── get-download-info.md
│   │   └── upload-file.md
│   ├── report-write/
│   │   ├── api-index.md
│   │   ├── submit.md
│   │   └── reply.md
│   ├── inbox/
│   │   ├── api-index.md
│   │   └── get-list.md
│   ├── outbox/
│   │   ├── api-index.md
│   │   └── get-list.md
│   ├── report-detail/
│   │   ├── api-index.md
│   │   └── get-info.md
│   ├── tasks/
│   │   ├── api-index.md
│   │   ├── get-page.md
│   │   └── get-simple-plan-and-report-info.md
│   ├── todos/
│   │   ├── api-index.md
│   │   ├── get-list.md
│   │   ├── complete.md
│   │   └── list-created-feedbacks.md
│   ├── templates/
│   │   ├── api-index.md
│   │   ├── get-list.md
│   │   └── list-by-ids.md
│   ├── plugin-report/
│   │   ├── api-index.md
│   │   ├── get-list.md
│   │   ├── get-latest-list.md
│   │   └── get-unread-list.md
│   ├── report-query/
│   │   ├── api-index.md
│   │   ├── get-todo-list.md
│   │   ├── get-unread-list.md
│   │   └── is-report-read.md
│   ├── report-message/
│   │   ├── api-index.md
│   │   ├── find-my-new-msg-list.md
│   │   └── read-report.md
│   ├── ai-qa/
│   │   ├── api-index.md
│   │   └── ask-sse.md
│   └── plan-create/
│       ├── api-index.md
│       └── create-simple.md
├── examples/
│   ├── user-search/README.md    # 含 3S1R 管理闭环
│   ├── employee-service/README.md # 含 3S1R 管理闭环
│   ├── file-service/README.md   # 含 3S1R 管理闭环
│   ├── report-write/README.md   # 含 3S1R 管理闭环（含写操作确认）
│   ├── inbox/README.md          # 含 3S1R 管理闭环
│   ├── outbox/README.md         # 含 3S1R 管理闭环
│   ├── report-detail/README.md  # 含 3S1R 管理闭环
│   ├── tasks/README.md          # 含 3S1R 管理闭环
│   ├── todos/README.md          # 含 3S1R 管理闭环（含写操作确认）
│   ├── templates/README.md      # 含 3S1R 管理闭环
│   ├── plugin-report/README.md  # 含 3S1R 管理闭环
│   ├── report-query/README.md   # 含 3S1R 管理闭环
│   ├── report-message/README.md # 含 3S1R 管理闭环（含写操作确认）
│   ├── ai-qa/README.md          # 含 3S1R 管理闭环（含 SSE 说明）
│   └── plan-create/README.md    # 含 3S1R 管理闭环（含写操作确认）
└── scripts/
    ├── user-search/
    │   ├── search-emp.py
    │   └── README.md
    ├── employee-service/
    │   ├── get-by-person-ids.py
    │   ├── get-org-info.py
    │   └── README.md
    ├── file-service/
    │   ├── get-download-info.py
    │   ├── upload-file.py
    │   └── README.md
    ├── report-write/
    │   ├── submit.py
    │   ├── reply.py
    │   └── README.md
    ├── inbox/
    │   ├── get-list.py
    │   └── README.md
    ├── outbox/
    │   ├── get-list.py
    │   └── README.md
    ├── report-detail/
    │   ├── get-info.py
    │   └── README.md
    ├── tasks/
    │   ├── get-page.py
    │   ├── get-simple-plan-and-report-info.py
    │   └── README.md
    ├── todos/
    │   ├── get-list.py
    │   ├── complete.py
    │   ├── list-created-feedbacks.py
    │   └── README.md
    ├── templates/
    │   ├── get-list.py
    │   ├── get-by-ids.py
    │   └── README.md
    ├── plugin-report/
    │   ├── get-list.py
    │   ├── get-latest-list.py
    │   ├── get-unread-list.py
    │   └── README.md
    ├── report-query/
    │   ├── get-todo-list.py
    │   ├── get-unread-list.py
    │   ├── is-report-read.py
    │   └── README.md
    ├── report-message/
    │   ├── find-my-new-msg-list.py
    │   ├── read-report.py
    │   └── README.md
    ├── ai-qa/
    │   ├── ask-sse.py
    │   └── README.md
    └── plan-create/
        ├── create-simple.py
        └── README.md
```

## 模块数量统计

| 分类 | 数量 | 说明 |
|------|------|------|
| 业务模块 | 15 | user-search / employee-service / file-service / report-write / inbox / outbox / report-detail / tasks / todos / templates / plugin-report / report-query / report-message / ai-qa / plan-create |
| API 接口文档 | 27 | 对两份主文档去重后形成的 27 个接口能力文档 |
| Python 脚本 | 27 | 与接口 1:1 映射 |
| 示例指引文档 | 15 | examples/<module>/README.md，含 3S1R 标准化流程 |
