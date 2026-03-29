# 分页查询汇报

**接口**: `POST /bp/task/relation/pageAllReports`  
**描述**: 根据任务 ID 分页查询该任务关联的所有汇报记录（含手动汇报和 AI 汇报）

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/task/relation/pageAllReports`

**Headers**:
```
appKey: <your-app-key>
Content-Type: application/json
```

**参数** (Body):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| taskId | string | 是 | BP 任务 ID（目标/KR/KI 均可） |
| keyword | string | 否 | 名称模糊搜索 |
| sortBy | string | 否 | 排序字段：`relation_time`（默认）/ `business_time` |
| sortOrder | string | 否 | 排序方向：`desc`（默认）/ `asc` |
| pageIndex | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，默认 `10` |

**请求体示例**:
```json
{
 "taskId": "2014631829004374017",
 "pageIndex": 1,
 "pageSize": 10
}
```

---

## 响应

**Schema**: `Result<PageInfo<TaskReportUnionVO>>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | PageInfo | 分页数据 |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### PageInfo 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| total | integer | 总记录数 |
| list | array | 汇报记录列表 |
| pageNum | integer | 当前页 |
| pageSize | integer | 每页数量 |
| size | integer | 当前页数量 |

### TaskReportUnionVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| type | string | 汇报类型：`manual` = 手动汇报，`ai` = AI 汇报 |
| main | string | 汇报标题 |
| content | string | 汇报正文（纯文本） |
| contentType | string | 正文类型：`html`（默认）/ `markdown` |
| writeEmpName | string | 写汇报人姓名 |

**响应示例**:
```json
{
 "resultCode": 1,
 "resultMsg": null,
 "data": {
 "total": 25,
 "list": [
 {
 "type": "manual",
 "main": "Q1 业绩周报",
 "content": "本周完成客户拜访 12 家，签约 2 家。",
 "contentType": "html",
 "writeEmpName": "张三"
 },
 {
 "type": "ai",
 "main": "AI 周报总结",
 "content": "根据本周数据分析，客户拜访进度良好。",
 "contentType": "html",
 "writeEmpName": "AI 助手"
 }
 ],
 "pageNum": 1,
 "pageSize": 10,
 "size": 2
 }
}
```

---

## 审计用途

**执行进度审计**：

### 1. 汇报频率分析
- 检查 `total` 汇报数量，识别"零汇报"任务
- 分析汇报周期是否与 `reportCycle` 匹配
- 识别长期无汇报的"静默"任务

### 2. 汇报内容质量
- 分析 `content` 内容是否具体、有数据支撑
- 识别"流水账"式汇报（无实质进展）
- 对比手动汇报与 AI 汇报的质量差异

### 3. 进度验证
- 结合汇报内容验证任务 `statusDesc` 是否真实
- 识别"报喜不报忧"的汇报
- 识别汇报与计划时间区间的偏差

### 4. GAP 分析辅助
- 通过汇报内容判断下级执行是否到位
- 识别"执行差"（汇报显示进度滞后）

---

## 脚本映射

无脚本，直接调用 API。

**注意**：如 `total > pageSize`，需多次调用获取全部汇报。
