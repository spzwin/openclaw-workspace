# 场景与接口对照 — 业务逻辑梳理

本文档说明：**在什么场景下会用到哪些接口**，以及**接口的调用顺序与数据用途**。

---

## 一、接口一览

| 接口 | 路径 | 用途 | 文档 |
|------|------|------|------|
| **chatListByPage** | `ai-huiji/meetingChat/chatListByPage` | 分页拉取会议列表（支持关键词、排序） | `openapi/meeting/chatListByPage.md` |
| **reportInfo** | `ai-huiji/report/reportInfo` | 获取单场会议的结构化报告（Markdown） | `openapi/meeting/reportInfo.md` |
| **checkSecondSttV2** | `ai-huiji/meetingChat/checkSecondSttV2` | 获取修正后的转写 + 发言人信息 | 见 api-index |
| **splitRecordList** | `ai-huiji/meetingChat/splitRecordList` | 获取实时/历史转写分片（无发言人） | `openapi/meeting/splitRecordList.md` |

**鉴权**：上述接口均在请求头携带 `appKey`，读取顺序见 `common/auth.md`。

---

## 二、按场景梳理：谁用谁、怎么用

### 场景 1：会议搜索与发现（列表 / 搜索 / 日期范围）

**用户意图示例**：  
「最近 4 条」「3 月 10 日的会议」「3 月 10 日到 3 月 15 日」「上个月」「搜索 OpenClaw」「正在进行的会议」

| 步骤 | 使用的接口 | 说明 |
|------|------------|------|
| 1 | **chatListByPage** | 唯一数据源。分页拉会议列表，可选 `nameBlur` 做关键词过滤。 |
| 2 | （客户端过滤） | 日期范围、进行中、最近 N 天：在 **chatListByPage** 返回的列表内，按 `create_time` / `combineState` 等做本地过滤。 |

**逻辑要点**：

- **最近 N 条**：`chatListByPage(pageNum=0, pageSize=N)`，直接取前 N 条。
- **最近 N 天 / 日期范围 / 单日 / 整月 / 上周 / 上个月**：不做分页扩展，最多仅拉 `chatListByPage(pageSize=10)`（最近 10 条会议），再按 `create_time` 转本地日期后过滤；若过滤后为空，引导用户使用「标题关键词搜索」（`nameBlur`）。
- **进行中的会议**：在列表结果中筛「当天」且 `combineState=0`，按开始时间倒序，优先推荐最新一条。
- **关键词搜索**：仅用接口 `nameBlur` 做会议名称模糊搜索，`chatListByPage(nameBlur=keyword, pageSize=10)`，最多返回 10 场，不做本地二次处理。

**不涉及**：reportInfo、checkSecondSttV2、splitRecordList。

---

### 场景 2：实时会议问答（时段回顾、谁说了什么、全文问答）

**用户意图示例**：  
「最近 30 分钟讲了什么」「开始后 20 分钟的内容」「有没有提到 XXX」「整个会议内容」

**前提**：已选定一场会议（会议 ID = `meeting_chat_id`）。

**接口与会议状态的关系（重要）**：

- **进行中会议**：只有 **splitRecordList** 能拿回实时原文，reportInfo / checkSecondSttV2 无数据。故进行中时**仅调用 splitRecordList**。
- **已结束会议**：reportInfo、checkSecondSttV2 才有数据；但存在**时间差**（刚结束尚未产出），此时仍用 **splitRecordList** 兜底取原文。

| 会议状态 | 使用的接口（顺序） | 说明 |
|----------|--------------------|------|
| 进行中 | **splitRecordList**（仅此一个） | 实时原文唯一数据源 |
| 已结束 | **reportInfo** → **checkSecondSttV2** → **splitRecordList** | 优先报告/修正转写；时间差时用 splitRecordList 兜底 |

**逻辑要点**：时间范围在拿到的 `records` 上做客户端过滤。回答形式：凡「某时间段/整场讲了什么」类提问一律**综合总结**，不按分钟/时间轴逐条展示；仅当用户明确要求「原文/谁说了什么」且数据来自 checkSecondSttV2 时，可格式化为「【MM:SS】发言人：内容」。

**代码入口**：`AIQA.get_full_meeting_content_sync(meeting_id, is_in_progress=None)` 先按状态分支，再按上表调接口；`answer_question(meeting_id, question, is_in_progress=None)` 在此基础上解析时间范围并生成提示词。

---

### 场景 3：单场会议总结（生成报告）

**用户意图示例**：  
「总结这场会议」「生成会议报告」

**接口与会议状态**：与场景 2 一致。**reportInfo 的 textReport 已是慧记侧大模型生成的结构化报告，直接返回，不再经本 skill 大模型二次总结；**仅当内容来自转写（checkSecondSttV2/splitRecordList）时才调大模型生成报告。

**逻辑要点**：报告模板、约束、禁止虚构等见 SKILL.md「会议总结报告的约束与模版」。**重新总结**时仍先按状态取内容（已结束优先 checkSecondSttV2/splitRecordList），再叠加用户要求 + 提示词重生成。

**代码入口**：`summarize_meeting(meeting_id, content=None, is_in_progress=None)`；未传 `content` 时内部按状态调 `get_full_meeting_content_sync`。

---

### 场景 4：待办事项提取

**用户意图示例**：  
「列一下待办」「有哪些要做的」「提取待办」

**接口与会议状态**：与场景 2、3 一致——进行中仅用 **splitRecordList**；已结束 **reportInfo → checkSecondSttV2 → splitRecordList**。与单场总结共用同一套内容获取逻辑（`get_full_meeting_content_sync`），最后一步改为「待办提取提示词」。待办约束与模版见 SKILL.md。

**代码入口**：`extract_todos(meeting_id, content=None, is_in_progress=None)`。

---

### 场景 5：多会议聚合总结

**用户意图示例**：  
「把这几场综合总结」「最近 3 场关于 XXX 的会议整体梳理」「XXX 话题最近讨论进展」

| 步骤 | 使用的接口 | 说明 |
|------|------------|------|
| 1 | **chatListByPage**（或已有列表结果） | 确定要汇总的 N 场会议（ID 列表）。 |
| 2 | 对**每一场**会议拉内容 | 按该场状态：**进行中仅用 splitRecordList**；**已结束**用 reportInfo → checkSecondSttV2 → splitRecordList，每场取一份内容。 |
| 3 | （无额外接口） | 将 N 场内容拼成「会议1 / 会议2 / …」的上下文，用「多会议聚合总结提示词」一次生成聚合报告。 |

**逻辑要点**：

- 内容长度控制：单场报告超 1500 字取前 1500；转写超 2000 字做均匀抽取约 2000 字。
- 聚合输出格式、议题演进、待办去重等见 SKILL.md「五、多会议聚合总结」。

---

## 三、内容获取：按会议状态分支（统一逻辑）

凡需要「单场会议正文」的能力（实时问答、单场总结、待办提取、多场聚合中的单场内容），都**先区分进行中 / 已结束**，再选接口：

- **进行中**：只有 **splitRecordList** 能拿回原文 → **仅调 splitRecordList**。
- **已结束**：reportInfo、checkSecondSttV2 才有数据；若存在**时间差**（刚结束尚未产出），用 **splitRecordList** 兜底。

```
进行中会议  →  splitRecordList（唯一有数据的接口）

已结束会议  →  reportInfo（有则用）
            →  checkSecondSttV2（无报告则用，含发言人）
            →  splitRecordList（时间差或前两者无数据时兜底，拿原文做总结/待办）
```

| 会议状态 | 接口顺序 | 说明 |
|----------|----------|------|
| 进行中 | splitRecordList | 实时原文唯一数据源 |
| 已结束 | reportInfo → checkSecondSttV2 → splitRecordList | 优先报告/修正转写；刚结束时间差时用 splitRecordList 取原文 |

---

## 四、小结表：场景 → 接口

| 场景 | 仅用 chatListByPage | 用 reportInfo | 用 checkSecondSttV2 | 用 splitRecordList |
|------|---------------------|---------------|----------------------|----------------------|
| 会议列表 / 搜索 / 日期范围 / 进行中 | ✅ | ❌ | ❌ | ❌ |
| 实时问答（要会议内容） | ❌ | 已结束时优先 | 已结束时其次 | 进行中仅用；已结束兜底 |
| 单场总结 | ❌ | 已结束时优先 | 已结束时其次 | 进行中仅用；已结束兜底 |
| 待办提取 | ❌ | 已结束时优先 | 已结束时其次 | 进行中仅用；已结束兜底 |
| 多场聚合 | ✅ 定范围 | 每场已结束时优先 | 每场已结束时其次 | 每场进行中仅用；每场已结束兜底 |

**记忆要点**：

- **只查列表、搜会议、按日期/进行中筛选** → 只用 **chatListByPage** + 本地过滤。
- **要某一场的「内容」**：**进行中只调 splitRecordList**；**已结束**再走 reportInfo → checkSecondSttV2 → splitRecordList（时间差时 splitRecordList 兜底）。
