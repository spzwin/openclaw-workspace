# BP 审计模块使用示例

**模块**: `audit`  
**目标用户**: AI Agent

---

## 触发条件

当用户请求涉及以下场景时，使用本模块：

- **获取周期**: "当前启用的 BP 周期是哪个？"、"获取 2026 年 Q1 的周期 ID"
- **获取分组**: "查看技术中心的分组结构"、"获取所有员工的分组 ID"
- **查询任务**: "查看张三的目标树"、"获取这个目标的完整信息"
- **审计 BP**: "审计这个 BP 是否符合规范"、"检查和上级的承接情况"
- **GAP 分析**: "做一下 GAP 分析"、"上下级之间有什么差异"

---

## 标准审计流程

### 场景 1：完整 BP 审计（四大模块）

```
步骤 1: 获取启用周期
  → GET /bp/period/getAllPeriod
  → 筛选 status=1，拿到 periodId

步骤 2: 获取目标分组
  → GET /bp/group/getTree?periodId={periodId}
  → 选择 type="personal" 或 type="org" 节点，拿到 groupId

步骤 3: 获取任务树（结构概览）
  → GET /bp/task/v2/getSimpleTree?groupId={groupId}
  → 检查 Goal+KR+KI 结构完整性

步骤 4: 获取目标详情（深入审计）
  → GET /bp/task/v2/getGoalAndKeyResult?id={目标 ID}
  → 分析：
    - 合规性：keyResults 是否非空？measureStandard 是否可衡量？
    - 向上承接：upwardTaskList 是否支撑上级意图？
    - 向下承接：downTaskList 是否覆盖本级 KI？

步骤 5: 查询汇报（执行验证）
  → POST /bp/task/relation/pageAllReports
  → 分析汇报频率、内容质量、进度真实性

步骤 6: 输出审计报告
  → 结构化呈现四大模块审计结果
```

### 场景 2：向上承接专项审计

```
步骤 1: 获取目标详情
  → GET /bp/task/v2/getGoalAndKeyResult?id={目标 ID}

步骤 2: 分析 upwardTaskList
  - 检查是否有向上对齐任务（无则标记"未承接"）
  - 逐个获取上级任务详情，对比目标/ KR/ KI 结构
  - 识别"挂羊头卖狗肉"（名称相似但实质无关）
  - 识别"衡量标准脱节"（上级要求 100 万，本级只承接 10 万）

步骤 3: 输出承接分析报告
```

### 场景 3：向下承接专项审计

```
步骤 1: 获取目标详情
  → GET /bp/task/v2/getGoalAndKeyResult?id={目标 ID}

步骤 2: 分析 downTaskList
  - 检查是否有向下对齐任务（无则标记"无人承接"）
  - 检查"部分悬空"（部分 KI 无下级承接）
  - 计算数值覆盖率（如收入指标）：
    覆盖率 = 下级汇总金额 / 本级目标金额 × 100%

步骤 3: 输出承接分析报告
```

### 场景 4：GAP 分析

```
步骤 1: 获取本级目标详情
  → GET /bp/task/v2/getGoalAndKeyResult?id={本级目标 ID}

步骤 2: 获取上级目标详情（从 upwardTaskList 拿 ID）
  → GET /bp/task/v2/getGoalAndKeyResult?id={上级目标 ID}

步骤 3: 获取下级目标详情（从 downTaskList 拿 ID）
  → GET /bp/task/v2/getGoalAndKeyResult?id={下级目标 ID}

步骤 4: 综合对比分析
  - 承接差：上级核心点是否在本级/下级中层层衰减？
  - 执行差：下级汇总能力是否足以支撑本级目标？
  - 逻辑差：上下级之间是否存在口径不一/理解断层？

步骤 5: 输出 GAP 分析报告
```

### 场景 5：快速定位审计对象

```
步骤 1: 搜索分组
  → GET /bp/group/searchByName?periodId={periodId}&name=技术部
  → 拿到 groupId

步骤 2: 搜索任务（可选）
  → GET /bp/task/v2/searchByName?groupId={groupId}&name=收入
  → 定位含"收入"的任务

步骤 3: 获取详情审计
  → GET /bp/task/v2/getGoalAndKeyResult?id={任务 ID}
```

---

## 审计检查清单

### 1. BP 合规性（基础）

| 检查项 | 检查方法 | 问题标记 |
|-------|---------|---------|
| 结构完整性 | keyResults 数组是否非空？每个 KR 的 actions 是否非空？ | "缺失 KR" / "缺失 KI" |
| 内容质量 | name/measureStandard 是否具体、可衡量？ | "描述模糊" / "不可衡量" |
| 逻辑自洽 | KI 是否能推导出 KR 达成？ | "逻辑断裂" |

### 2. 向上承接

| 检查项 | 检查方法 | 问题标记 |
|-------|---------|---------|
| 对齐正确性 | upwardTaskList 是否非空？对比上下级目标/ KR/ KI | "未承接" / "方向偏移" |
| 对齐完整性 | 上级核心 KR 是否全部承接？ | "选择性承接" / "职责盲区" |

### 3. 向下承接

| 检查项 | 检查方法 | 问题标记 |
|-------|---------|---------|
| 正确性 | downTaskList 是否对应本级 KI？ | "承接错误" |
| 完整性 | 本级 KI 是否全部有下级承接？ | "部分悬空" / "协作断裂" |
| 数值覆盖率 | 下级汇总金额 / 本级目标金额 | "覆盖率不足 XX%" |

### 4. GAP 分析

| 检查项 | 检查方法 | 问题标记 |
|-------|---------|---------|
| 承接差 | 上级核心点是否层层衰减？ | "承接衰减" |
| 执行差 | 下级汇总能力是否支撑本级？ | "执行缺口" |
| 逻辑差 | 上下级口径是否一致？ | "理解断层" |

---

## 注意事项

1. **ID 精度**：所有 ID 使用 string 类型，严禁 parseInt/Number 转换
2. **分组 ID vs 员工 ID**：注意区分，`getPersonalGroupIds` 入参是员工 ID，返回 value 是分组 ID
3. **递归遍历**：任务树/分组树为递归结构，需递归处理 children
4. **分页查询**：汇报接口如 total > pageSize，需多次调用
5. **周期状态**：优先选择 status=1（启用）的周期
