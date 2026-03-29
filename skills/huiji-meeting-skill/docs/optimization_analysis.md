# huiji-meeting-skill v2.0 优化建议 — 分析与沟通

以下是对「优化建议清单」的逐条分析，以及需要和你对齐的结论；**未改任何现有代码**，只做确认与澄清。

---

## 1. AI 生成回退给 Agent（高优先级）

**建议**：当未配置 OPENAI 时，不输出 fallback 文案，而是返回结构化数据（如 `{fallback, task, content, system_prompt}`），由 OpenClaw Agent 自行生成报告/待办。

**分析**：
- **合理**。当前 fallback 是一段「说明 + 提示词摘要」，Agent 拿不到完整 content + 完整 system_prompt，无法代劳生成。
- **注意**：`generate_meeting_report` / `generate_todo_list` 若改为返回 `str | dict`，所有调用方都要兼容：
  - **main.py**：`summarize_meeting()` / `extract_todos()` 需判断：若得到 dict，则原样返回或按约定交给上层（Agent 取到后自己调 LLM）；CLI 场景若直接 `print(result)`，dict 会变成 repr，可约定「当 fallback 时返回的 dict 由 Agent 解析，CLI 可打印一句“未配置 LLM，已返回原始内容与提示词供 Agent 使用”」。
- **建议实现**：ai_provider 在 _call_llm 为 None 时返回 dict；main.py 判断若为 dict 则 return 该 dict（或序列化为 JSON 字符串），由上层 Agent 识别并处理。

**结论**：建议采纳；实现时约定「返回 dict 时的字段与语义」，并让 main 层透传/序列化给 Agent。

---

## 2. 多关键词 AND 搜索（高优先级）

**建议**：用户输入「希笛尼 消化不良」时拆成多词，要求**每个关键词**至少命中一个字段（AND），再按各词得分加总排序。

**分析**：
- **合理**。当前把整句当一个 keyword 做子串匹配，无法表达「同时包含 A 和 B」。
- 实现要点：
  - 关键词拆分：按空格拆，过滤空串；若只得到一个词，行为与现有一致。
  - AND 逻辑：对每个会议，对每个 keyword 算一次单词得分（keywordList+3, name+2, tidyText+1, summary+1）；若任一 keyword 得分为 0 则该会议不命中；否则总分为各 keyword 得分之和，按总分排序。

**结论**：建议采纳。

---

## 3. 时长显示策略（中优先级）— 需要和你对齐

**建议**：对时长做「合理性校验」：用 meetingLength 与 (finishTime - createTime) 的差异判断是否标「含暂停」、是否隐藏异常 finishTime。

**你的疑问**：已结束会议大概率有 meetingLength；用「完成时间减开始时间」只是在**没有 meetingLength** 或**该字段没有**的时候。你不确定具体该怎么改。

**建议的明确逻辑（请你确认是否按这个做）**：

- **情况 A：有 meetingLength（绝大多数已结束会议）**
  - **展示**：时长以 **meetingLength** 为准（现有逻辑不变）。
  - **校验**：若同时有 createTime、finishTime，可算出「时间跨度」span = finishTime - createTime（毫秒）。  
    - 若 span 与 meetingLength 差异较大（例如 |span - meetingLength| > 0.2 * meetingLength，即差超过 20%）：在时长旁加标记，如「⏱️ 34分7秒（含暂停）」。
    - 若 span 极端异常（例如 span > meetingLength 的 10 倍）：视为 finishTime 可能被污染，**不再展示结束时间**，只展示时长，避免误导。
  - 这样「完成时间减开始时间」只用于**校验**，不替代 meetingLength 作为主时长。

- **情况 B：没有 meetingLength（或为 0/空）**
  - 此时没有「两数对比」，无法做差异校验。
  - **展示**：若有 createTime 和 finishTime，用 **finishTime - createTime** 得到时间跨度，格式化为「X分Y秒」作为时长展示；若没有起止时间，则展示「时长: (未知)」。
  - finishTime 有则照常展示，不做「10 倍」隐藏（因为缺 meetingLength 时没有参照）。

**需要你确认**：
1. 是否同意：**有 meetingLength 时**仅用 finishTime - createTime 做校验（差异大标「含暂停」、极端异常不展示 finishTime）？  
2. 是否同意：**没有 meetingLength 时**用 finishTime - createTime 推导时长，能算就展示，不能算就「(未知)」？  
3. 若同意，再在 client 的 `_format_meeting_item` 里把 createTime/finishTime 的毫秒数或 span 带给 formatter（或 formatter 自己从 create_time/finish_time 的 ISO 转毫秒再算），以便 formatter 只做展示与标记逻辑。

---

## 4. 时区严谨化（中优先级）

**建议**：`get_in_progress_meetings()` 里用 `zoneinfo.ZoneInfo("Asia/Shanghai")` 得到「当天」，避免依赖系统时区。

**分析**：
- **合理**。当前 `datetime.now().date()` 和 `astimezone()` 依赖本机时区，不同环境可能不一致。
- 若技能主要面向国内用户，写死 `Asia/Shanghai` 简单可靠；若需支持海外，可后续改为配置项。

**结论**：建议采纳；先写死 Asia/Shanghai，必要时再配置化。

---

## 6. ASR 提示词去重（低优先级）

**建议**：`AI_QA_SYSTEM_PROMPT` 与 SKILL.md 里的「ASR 转写噪音处理」内容集中维护，避免两边改一边忘。

**分析**：
- **合理**。但「从 SKILL.md 动态读取」会依赖路径、编码，运行时读 Markdown 也略重。
- **更稳妥做法**：以 **prompts.py 为唯一来源**，ASR 段落只维护一份；SKILL.md 里该节写一句「与 prompts.py 中 AI_QA_SYSTEM_PROMPT 的 ASR 转写噪音处理段落一致」，或贴简短摘要 + 引用文件路径。这样不增加运行时依赖，只做文档同步约定。

**结论**：建议采纳「单一来源」思路，优先以 prompts.py 为准，SKILL.md 引用说明即可。

---

## 优先级与改动量（保持原表）

| # | 建议           | 文件              | 优先级 | 改动量 |
|---|----------------|-------------------|--------|--------|
| 1 | AI 回退给 Agent | ai_provider, main | 高     | 小     |
| 2 | 多关键词 AND   | intent.py         | 高     | 中     |
| 3 | 时长异常检测   | formatter, client | 中     | 中（逻辑已在上文拆清） |
| 4 | 时区严谨化     | client.py         | 中     | 小     |
| 6 | ASR 提示词去重 | prompts, SKILL   | 低     | 小     |

---

**下一步**：请你主要确认 **第 3 点** 的 A/B 两套逻辑是否符合你的预期；确认后可按该方案改 client + formatter，其余几点按上表顺序实现即可。
