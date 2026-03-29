# 获取关键举措详情

**接口**: `GET /bp/task/v2/getAction`  
**描述**: 根据关键举措 ID 获取关键举措的完整详情

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/task/v2/getAction`

**Headers**:
```
appKey: <your-app-key>
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| id | string | 是 | 关键举措 ID（来自 `4.4 查询任务树` 或 `4.5/4.6` 返回的 `actions[].id`） |

---

## 响应

**Schema**: `Result<ActionVO>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | ActionVO | 关键举措详情（继承 BaseTaskVO） |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### BaseTaskVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 任务 ID |
| groupId | string | 所属分组 ID |
| name | string | 任务名称 |
| statusDesc | string | 任务状态（草稿/未启动/进行中/已关闭） |
| reportCycle | string | 汇报周期 |
| planDateRange | string | 计划时间区间 |
| taskUsers | array | 任务参与人列表 |
| taskDepts | array | 任务参与部门列表 |
| upwardTaskList | array | **向上对齐任务**（审计用） |
| downTaskList | array | **向下对齐任务**（通常为空） |
| path | string | 路径 |
| fullLevelNumber | string | 任务完整编码 |

---

## 审计用途

**KI 层级专项审计**：

### 1. 内容质量检查
- 检查 `name` 是否具体、有明确行动指向
- 识别模糊描述（如"加强"、"推进"无具体动作）
- 检查 `planDateRange` 是否有明确时间约束

### 2. 责任人检查
- 检查 `taskUsers` 是否有"承接人"角色
- 识别"无人负责"的悬空 KI

### 3. 向上对齐验证
- 检查 `upwardTaskList`，验证本 KI 是否对应上级 KR
- 识别"方向偏移"（KI 与上级 KR 无关）

### 4. 状态分析
- 检查 `statusDesc`，识别长期"未启动"或"已关闭"的 KI
- 结合 `planDateRange` 识别延期风险

---

## 脚本映射

无脚本，直接调用 API。
