# 获取目标详情

**接口**: `GET /bp/task/v2/getGoalAndKeyResult`  
**描述**: 根据目标 ID 获取目标的完整详情，包含该目标下的所有关键成果及关键举措

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/task/v2/getGoalAndKeyResult`

**Headers**:
```
appKey: <your-app-key>
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| id | string | 是 | 目标 ID（来自 `4.4 查询任务树` 中 `type="目标"` 的节点 `id`） |

---

## 响应

**Schema**: `Result<GoalAndKeyResultVO>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | GoalAndKeyResultVO | 目标详情（继承 BaseTaskVO） |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### BaseTaskVO 公共字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 任务 ID |
| groupId | string | 所属分组 ID |
| name | string | 任务名称 |
| statusDesc | string | 任务状态（草稿/未启动/进行中/已关闭） |
| reportCycle | string | 汇报周期（如 `week+1`） |
| planDateRange | string | 计划时间区间（`yyyy-MM-dd ~ yyyy-MM-dd`） |
| taskUsers | array | 任务参与人列表 |
| taskDepts | array | 任务参与部门列表 |
| upwardTaskList | array | **所有向上对齐任务**（审计用） |
| downTaskList | array | **所有向下对齐任务**（审计用） |
| path | string | 路径 |
| fullLevelNumber | string | 任务完整编码 |

### GoalAndKeyResultVO 特有字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| keyResults | array | 关键成果列表（每个含 `actions` 关键举措列表） |

### KeyResultVO 结构

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 关键成果 ID |
| name | string | 关键成果名称 |
| measureStandard | string | **衡量标准**（审计重点） |
| statusDesc | string | 状态 |
| actions | array | 关键举措列表 |

### ActionVO 结构

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 关键举措 ID |
| name | string | 关键举措名称 |
| statusDesc | string | 状态 |

---

## 审计用途

**核心审计接口**，支持全部四大审计模块：

### 1. BP 合规性审计
- **结构完整性**：检查 `keyResults` 数组是否非空，每个 KR 的 `actions` 是否非空
- **内容质量**：分析 `name`、`measureStandard` 是否具体、可衡量
- **逻辑自洽**：分析 KI（actions）是否能推导出 KR 达成

### 2. 向上承接审计
- **对齐正确性**：检查 `upwardTaskList`，验证本级目标是否支撑上级意图
- **对齐完整性**：识别是否有"选择性承接"（回避核心难题）

### 3. 向下承接审计
- **执行条件**：检查 `downTaskList` 是否非空
- **正确性**：下级任务是否对应本级关键举措
- **数值专项**：针对收入/利润指标，计算数值覆盖率

### 4. GAP 分析
- 综合对比 `upwardTaskList`、本级内容、`downTaskList`
- 识别承接差、执行差、逻辑差

---

## 脚本映射

无脚本，直接调用 API。
