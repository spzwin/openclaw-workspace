# 获取关键成果详情

**接口**: `GET /bp/task/v2/getKeyResult`  
**描述**: 根据关键成果 ID 获取关键成果的完整详情，包含该关键成果下的所有关键举措

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/task/v2/getKeyResult`

**Headers**:
```
appKey: <your-app-key>
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| id | string | 是 | 关键成果 ID（来自 `4.4 查询任务树` 或 `4.5 获取目标详情` 返回的 `keyResults[].id`） |

---

## 响应

**Schema**: `Result<KeyResultVO>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | KeyResultVO | 关键成果详情（继承 BaseTaskVO） |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### BaseTaskVO 公共字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 任务 ID |
| groupId | string | 所属分组 ID |
| name | string | 任务名称 |
| statusDesc | string | 任务状态 |
| reportCycle | string | 汇报周期 |
| planDateRange | string | 计划时间区间 |
| taskUsers | array | 任务参与人列表 |
| upwardTaskList | array | **向上对齐任务**（审计用） |
| downTaskList | array | **向下对齐任务**（审计用） |
| fullLevelNumber | string | 任务完整编码 |

### KeyResultVO 特有字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| measureStandard | string | **衡量标准**（审计重点） |
| actions | array | 关键举措列表 |

### ActionVO 结构

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 关键举措 ID |
| name | string | 关键举措名称 |
| statusDesc | string | 状态 |
| upwardTaskList | array | 向上对齐任务 |
| downTaskList | array | 向下对齐任务 |

---

## 审计用途

**KR 层级专项审计**：

### 1. 衡量标准检查
- 检查 `measureStandard` 是否具体、可量化
- 识别模糊描述（如"提升"、"优化"无具体指标）

### 2. KI 覆盖完整性
- 检查 `actions` 数组是否非空
- 分析 KI 数量是否足以支撑 KR 达成
- 识别"有 KR 无 KI"的悬空情况

### 3. 向下承接审计
- 检查 `downTaskList`，验证下级是否承接了本 KR
- 计算数值覆盖率（如收入/利润指标）

### 4. 向上对齐验证
- 检查 `upwardTaskList`，验证本 KR 是否对应上级目标的 KI

---

## 脚本映射

无脚本，直接调用 API。
