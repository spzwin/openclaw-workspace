---
name: pharma-province-report
description: >
  省级市场分析**单章节**报告生成器。给定省份名称、章节文件夹（含 模版.md 和 检索指南.md），
  按两步执行：Step 1 逐模块执行联网搜索或 CLI 数据查询；Step 2 严格按模板结构填充生成章节报告.md。
  触发场景：用户说"帮我生成XX省的X.X章节"、"跑一下1.2章节"、"执行章节报告工作流"。
---

# 单章节省级报告生成工作流

## 参考资料

执行前读取 `pharma-province-report-skill/references/` 下所有文件作为背景知识：
- `莫诺菲_产品基础信息.md` / `科莫非_产品基础信息.md`：产品知识，Step 2 填写产品变量时使用
- `schema.json` / `product_mapping.json` / `field_mapping.json`：CLI 字段语义，理解 CLI 输出时使用
- **`hospital_data_cli_字段与命令说明.md`**：CLI 核心字段含义、流向三态语义、枚举值域、省份缩写表、各章节常用命令——Step 1 路径B 执行前必读

## 输入

| 参数 | 说明 | 默认值 |
|---|---|---|
| **省份** | 目标省份，如 `广东省` | 必填 |
| **章节文件夹路径** | 含 `模版.md` 和 `检索指南.md` 的章节目录 | 必填 |
| **Excel路径** | hospital_base.xlsx 的路径 | `pharma-province-report-skill/references/hospital_base.xlsx` |

若参数未提及，先询问用户，全部确认后再执行。

**章节ID** 由章节文件夹名自动推断（如 `1.2、全省患者地理分布与渠道结构` → 章节ID `1.2`）。

## 输出结构

所有输出路径均相对于 **workspace 根目录**（即 `skills/` 父级目录）。`省份报告/` 与 `skills/` 同级，不是与各 skill 子文件夹同级。

```
{workspace根目录}/
├── skills/
│   ├── pharma-province-report-skill/   ← 本 skill 所在位置
│   └── pharma-province-assemble-skill/
└── 省份报告/                            ← 输出写入此处（与 skills/ 同级）
    └── {省份}/
        └── {章节ID}_{章节名}/
            ├── 搜索结果/
            │   ├── 01_{模块名}/
            │   │   └── 搜索结果.md
            │   └── 02_{模块名}/
            │       └── CLI数据.json
            └── 报告.md
```

> 章节模版文件夹（含 `模版.md` 和 `检索指南.md`）由调用时通过**章节文件夹路径**参数传入，不在 workspace 目录中。

---

## Step 1 — 数据采集（联网搜索 + CLI查询）

1. 读取章节文件夹中的 `检索指南.md`，提取每个模块的编号、名称、**来源类型**

2. 根据 `来源类型` 分两条路径执行：

### 路径A：`来源类型 = 联网搜索`

- 使用检索指南中的检索词执行 WebSearch（多条查询词并行）
- 汇总数值、来源 URL、关键文段
- 写入 `搜索结果/{编号}_{模块名}/搜索结果.md`

格式：
```markdown
# [模块名称]

## 检索词
[本模块使用的查询词列表]

## 来源 URL
<!-- ⚠️ 铁律：每条使用过的网页来源必须列出完整可访问 URL，格式为 Markdown 链接，供合并时汇总引用 -->
- [来源名称或标题](https://完整URL)
- [来源名称或标题](https://完整URL)

## 原文摘录
[关键原文段落或数据]

## 提取数据
| 指标 | 数值 | 来源 | 备注 |
|---|---|---|---|

## 省级估算（如适用）
估算公式 / 假设说明 / 结果
```

> **估算原则**：无法直接搜索的省级数值须基于全国数据推算，明确标注估算公式和口径，不得写成官方事实。
>
> **URL 保存铁律**：联网搜索模块的「来源 URL」节必须列出所有实际访问过的网页完整 URL（`https://...`），不得只写网站名称或省略链接。这是后续合并报告自动生成可点击参考文献的数据来源。

### 路径B：`来源类型 = CLI查询`

- 读取检索指南中的 `CLI命令` 字段
- 将占位符替换为实际值：`{province}` → 目标省份，`{excel_path}` → Excel路径，`{province_short}` → 省份缩写（如广东→GD）
- 执行命令：

```bash
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  --query-id "HDQ-{province_short}-{chapter_id}-{module_id}" \
  --query-output-dir "省份报告/{province}/{chapter_id}_{chapter_name}/搜索结果/{module_name}" \
  {subcommand} --省 "{province}" [其他参数]
```

- 将 CLI 输出的 JSON 保存至 `搜索结果/{编号}_{模块名}/CLI数据.json`
- **CLI执行规则**：串行执行，不并发；同一模块的多条命令按顺序逐条执行

3. 完成后告知：`✅ Step 1 完成，X 个模块（Y 联网搜索 / Z CLI查询）已保存至 省份报告/{省份}/{章节ID}_{章节名}/搜索结果/`

---

## Step 2 — 按模板生成章节报告

1. 读取：
   - 章节文件夹中的 `模版.md`
   - 所有搜索结果（`搜索结果.md` 和 `CLI数据.json`）
   - `pharma-province-report-skill/references/` 下的产品参考资料

2. **以「复制→替换」方式生成报告（严禁「理解→重写」）：**

   **【前置步骤：建立本章参考文献编号表】**（必须在写报告正文前完成，不可跳过）

   从本章节 Step 1 收集的所有 `搜索结果.md` 文件的「来源 URL」节中，提取所有 URL，去重，按首次出现顺序编号。在对话中（不写入文件）先输出完整编号表：

   ```
   [1](https://...) 来源名称或页面标题
   [2](https://...) 来源名称或页面标题
   [3](https://...) 来源名称或页面标题
   ```

   **参考文献格式铁律（逐条严格执行）：**

   ✅ 正确格式 — 编号是超链接，每条之间必须有**空行**：
   ```
   [1](https://tjj.hunan.gov.cn/...) 湖南省统计局年鉴

   [2](https://pmc.ncbi.nlm.nih.gov/...) GBD 2023贫血负担研究

   [3](https://www.sohu.com/...) 湖南省2024年统计公报
   ```

   ❌ 严禁以下所有错误格式：
   ```
   [1] https://... 名称          ← 编号与URL分离，[1]不可点击，禁止
   1. https://... 名称           ← 使用序号而非超链接编号，禁止
   [1](https://...) 名称\n[2](https://...) 名称   ← 无空行，Markdown会渲染成一行，禁止
   （内部数据，query_id: HDQ-...） ← 内部数据禁止出现在参考文献列表中
   ```

   **`{references}` 必须填写，每个章节都不得跳过或留空：**

   | 情况 | 填写内容 |
   |---|---|
   | 有联网搜索 URL | 按格式填入编号列表，每条之间空行 |
   | 无任何 URL（纯CLI章节） | 填写：`> 本章节数据均来自内部数据库，无联网检索来源。` |

   **内部数据与URL来源的严格分离（违反视为错误）：**
   - `{references}` 中**只放 URL 来源**，格式为 `[n](https://完整URL) 来源名称`，每条之间空行
   - `（内部数据，query_id: HDQ-...）` **只在正文行内**出现，**绝对禁止**写入 `{references}`
   - 两者完全分离，不得混入

   **引用准确性铁律（严禁违反）：**
   - 编号表确定后不得再改变，正文中只使用表中已有编号
   - 严禁先写正文再凑编号
   - 严禁同一 URL 用两个不同编号；严禁不同 URL 共用同一编号
   - 严禁凭空捏造未出现在搜索结果中的 URL

   操作顺序：
   a. 先将 `模版.md` 的全部内容**逐字复制**到 `报告.md` 中
   b. 再对每个 `{variable}` 找到对应数据并替换

   > **心智提示**：你在做的是【替换变量】，不是【重新撰写报告】。模版结构就是最终报告结构，不得因为数据丰富或想"改善结构"而改变它。

**报告输出铁律：**
- **标题 `#` 数量铁律**：每个标题前面的 `#` 数量必须与模版完全相同。例如模版写 `### 6.1`，报告也必须写 `### 6.1`，绝对不得写 `# 6.1` 或 `## 6.1`，即使章节内容再丰富也不例外
- **子节命名铁律**：子节的编号和名称必须与模版一字不差，禁止重命名、重排、合并或拆分。例如 `#### 3.3.6 各市医保差异` 不得改为 `#### 3.3.5 各市医保差异` 或 `#### 各市报销差异`
- 章节标题、顺序、表格结构、Blockquote、分隔线——全部原样保留
- 只替换 `{variable}`，不增、不删、不移动模版中的任何一行
- **内部数据字段（含 `internal_` 前缀或注明"内部数据依据"的字段）必须来自 CLI JSON，不得凭空填写**

变量填写规则：
- 有 URL 来源的数据 → 数值后紧跟 `[n]`，`n` 对应前置编号表中该 URL 的编号
- CLI JSON 数据 → 标注 `（内部数据，query_id: HDQ-...）`，不占用 `[n]` 编号
- `{references}` → 填入前置步骤建立的完整编号表，格式为每行 `[n](https://...) 来源名称`
- 需估算 → 填结果 + 括号内注明估算口径
- 无数据 → 填 `暂无直接数据，建议查阅[推荐来源]`，不得虚构 `[n]`

**行内引用示例**（`[n]` 紧跟数值，不独占一行）：

| 模版变量 | 填充后示例 |
|---|---|
| `{resident_population}` | `1.27 亿人（2023年）[1]` |
| `{ida_prevalence_rate}` | `约 14.8%（估算，基于全国均值）[2]` |
| `{internal_top_hospitals}` | `前20家医院IDA患者合计约 8.2 万（内部数据，query_id: HDQ-GD-1.4-B01）` |
| `{references}` | `[1](https://stats.gov.cn/...) 国家统计局2023年统计年鉴` （空行） `[2](https://pubmed.ncbi...) 中国贫血流行病学研究` |

3. 报告写完后，在**对话消息中**（不写入报告文件）输出反思核查：

```
📋 反思核查 — {省份} / {章节ID} {章节名}
1. 遗留占位符：[无 / 列出位置]
2. 模板结构完整性：[逐条确认标题/表格/Blockquote]
3. CLI数据字段核验：[每个 internal_ 字段是否均来自 JSON]
4. 强证据字段：[直接搜索/CLI数据]
5. 估算字段：[已标注口径]
6. 数据薄弱区域：[建议补充来源]
7. 标题层级核验：[逐条对比每个标题的 # 数量是否与模版一致；列出所有不一致处并说明如何修正]
```

完成后告知：`✅ 章节报告已生成：省份报告/{省份}/{章节ID}_{章节名}/报告.md`

---

## 检索指南 来源类型 规范（供参考）

检索指南中每个模块必须声明：

**联网搜索模块**：
```markdown
**来源类型**: `联网搜索`
```

**CLI查询模块**：
```markdown
**来源类型**: `CLI查询`
**目标变量**: `{var1}`, `{var2}`
**CLI命令**:
```bash
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  --query-id "HDQ-{province_short}-{chapter_id}-{module_id}" \
  --query-output-dir "省份报告/{province}/{chapter_id}_{chapter_name}/搜索结果/{module_name}" \
  {subcommand} --省 "{province}"
```
**说明**: [业务含义]
```

---

## 执行约束

- CLI 脚本路径：`pharma-province-report-skill/scripts/hospital_data.py`
- Excel 默认路径：`pharma-province-report-skill/references/hospital_base.xlsx`
- CLI 必须串行执行（同一省份不并发）
- 报告中内部数字必须可通过 `query_id` 追溯到对应 JSON 文件
- 退货医院（flow < 0）不算入机会点，使用 `--flow-status uncovered`（严格 flow == 0）
