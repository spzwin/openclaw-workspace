# hospital_data_cli 字段与命令说明

> 本文档提炼自 `hospital_data_cli_standard_skill/SKILL.md`，仅保留在省级报告 Skill 执行中需要直接使用的内容。
> 执行 Step 1 路径B（CLI查询）前必读。

---

## 核心数值字段

| 字段 | 含义 | 单位 | 关键提示 |
|---|---|---|---|
| IDA患者数 | 缺铁性贫血患者数估算 | 人 | 医院 IDA 患者池规模；0 通常表示新建医院或待补核 |
| 莫诺菲流向 | 已在院产生销售的莫诺菲数量 | 支（500mg/支） | **正数=正常销售；零=严格未覆盖；负数=退货异常** |
| 科莫非流向 | 已在院产生销售的科莫非数量 | 支（100mg/支） | 同上 |

---

## 流向三态语义（重要）

`--flow-status` 支持四种取值：

| 状态 | 数学定义 | 业务含义 |
|---|---|---|
| `covered` | flow > 0 | 已覆盖正常销售 |
| `uncovered` | flow == 0（严格） | **严格未覆盖**，是真正的开发机会 |
| `returned` | flow < 0 | 已覆盖但产生退货异常，需单独追溯，**不算机会点** |
| `not-covered` | flow ≤ 0 | 兼容旧脚本，已不推荐 |

> **规则**：报告章节中"机会点"分析只用 `--flow-status uncovered`（严格 flow == 0），退货医院不计入。

---

## 枚举字段值域

**客户性质**（2类）：`公立医院` / `民营医疗`

**客户级别**（12类）：
```
三级甲等  三级乙等  三级丙等  三级
二级甲等  二级乙等  二级丙等  二级
一级及其他  社区医院  乡镇医院  诊所
```

**医院级别大类**（3类，用于分层汇总）：
```
三级       → 学术高端线
二级医院    → 区域中坚
一级及其他  → 县域基层 + 民营 + 社区 + 乡镇
```

**类型名称**：`综合` / `专科` / `基层医疗`

---

## 支持的筛选参数

```
--大区   --区域   --省   --市   --区县
--客户名称   --客户性质   --类型名称
--客户级别   --医院级别大类
```

---

## 常用命令速查

### 总览
```bash
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  summary --省 "{province}"
```

### 分组汇总
```bash
# 按市分组
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  group --by 市 --省 "{province}"

# 按医院级别大类分组
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  group --by 医院级别大类 --省 "{province}"

# 按类型名称分组
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  group --by 类型名称 --省 "{province}"
```

### 排名查询
```bash
# 按医院名排名（IDA患者数 Top 20）
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  rank --by 客户名称 --metric IDA患者数 --省 "{province}" --top 20

# 按医院名排名（Top 10，用于5.2重点医院）
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  rank --by 客户名称 --metric IDA患者数 --省 "{province}" --top 10
```

### 产品对比
```bash
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  product-compare --省 "{province}"
```

### 明细查询
```bash
# 已覆盖医院明细（flow > 0）
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  detail --省 "{province}" --产品 "莫诺菲" --flow-status covered \
  --sort-by IDA患者数 --desc --top 20

# 严格未覆盖高潜医院（flow == 0）
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  detail --省 "{province}" --产品 "莫诺菲" --flow-status uncovered \
  --sort-by IDA患者数 --desc --top 20
```

### 单医院查询
```bash
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  hospital --name "{hospital_name}"

python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  hospital --name "{hospital_keyword}" --fuzzy
```

### 机会点分析
```bash
# 未覆盖高潜医院
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  opportunity --type uncovered-high-potential --产品 "莫诺菲" --省 "{province}" --top 20

# 退货医院追溯（单独处理，不计入机会点）
python pharma-province-report-skill/scripts/hospital_data.py \
  --excel "pharma-province-report-skill/references/hospital_base.xlsx" \
  opportunity --type returned-followup --产品 "莫诺菲" --省 "{province}" --top 20
```

---

## 各章节 CLI 命令对应关系

| 章节 | 主要 CLI 子命令 | 说明 |
|---|---|---|
| 1.2 | `summary`、`group --by 市`、`product-compare`、`group --by 医院级别大类` | 患者地理分布与渠道结构 |
| 1.4 | `rank --top 20`、`summary`、`product-compare` | 服务提供者总览 |
| 2.2 | `group --by 医院级别大类`、`group --by 类型名称`、`product-compare` | 治疗渠道分布 |
| 3.1 | `product-compare`、`summary` | 竞争格局 |
| 5.1 | `group --by 医院级别大类`、`group --by 市`、`summary` | 医疗体系概览 |
| 5.2 | `rank --top 10`、`hospital --name`、`opportunity` | 重点医院深度拆解 |
| 6.1–6.6 | `rank --top 20`、`detail --flow-status covered` | 六大科室逐院分析 |

---

## 省份缩写对照表（用于 query-id）

| 省份 | 缩写 | 省份 | 缩写 |
|---|---|---|---|
| 广东省 | GD | 浙江省 | ZJ |
| 江苏省 | JS | 上海市 | SH |
| 北京市 | BJ | 湖南省 | HN |
| 湖北省 | HB | 四川省 | SC |
| 山东省 | SD | 河南省 | HA |
| 福建省 | FJ | 广西壮族自治区 | GX |
| 安徽省 | AH | 云南省 | YN |
| 江西省 | JX | 陕西省 | SN |
| 贵州省 | GZ | 重庆市 | CQ |
| 辽宁省 | LN | 河北省 | HE |
| 吉林省 | JL | 黑龙江省 | HLJ |
| 山西省 | SX | 内蒙古自治区 | NMG |
| 新疆维吾尔自治区 | XJ | 西藏自治区 | XZ |
| 甘肃省 | GS | 青海省 | QH |
| 宁夏回族自治区 | NX | 海南省 | HI |
| 天津市 | TJ | | |

---

## 产品字段名与展示名

CLI 查询、query_id、JSON 字段名均使用真实字段名：

| CLI字段名 | 报告展示名 |
|---|---|
| `莫诺菲` | 莫诺菲（异麦芽糖酐铁） |
| `科莫非` | 科莫非（右旋糖酐铁） |

---

## 执行约束

1. **串行执行**：同一省份的多条 CLI 命令必须串行，不允许并发操作同一 Excel 文件
2. **query-id 唯一性**：同一 query_id 对应的 JSON 必须与命令行完全一致；参数变更时覆盖旧 JSON 或换新 query_id
3. **内部数字零容错**：报告中凡出现省/市/医院级别的流向数据、IDA患者数，必须来自 CLI JSON，不得 AI 自行估算
4. **flow-status 严格性**：机会点只用 `uncovered`（flow == 0），退货医院（flow < 0）单独用 `returned-followup` 处理
