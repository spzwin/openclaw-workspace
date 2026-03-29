# 工作协同脚本异常分析（2026-03-28）

## 1. templates/get-list.py 默认返回 `data=null`

### 现象
- 直接执行 `python3 scripts/templates/get-list.py --limit 5`
- 平台返回：`resultCode=1, data=null`

### 复测结果
- 扩大时间窗口后，接口正常返回事项列表：
  - `beginTime=1704038400000`
  - `endTime=1774991999000`

### 结论
- 不是接口硬错误，更像是默认“最近时间窗口”内没有最近处理事项。
- 平台在空结果场景下返回 `data=null`，而不是空数组。

### 已处理
- 脚本已把成功场景下的 `data=null` 归一化为：
  - `{"recentOperateTemplates":[]}`
- `scripts/templates/README.md` 已补充时间窗口说明。

## 2. ai-qa/ask-sse.py 返回 SSE JSON 片段拼接串

### 现象
- 原脚本把每个 `data:` 事件直接字符串拼接。
- 输出中的 `answer` 混入了：
  - `{"content":"..."}` 片段
  - `{"id":"firstTextDelay"...}` 指标事件
  - `ok`

### 结论
- 这是脚本聚合逻辑问题，不是平台接口错误。
- 平台返回的是标准 SSE 事件流，内容事件和指标事件混在一起。

### 已处理
- 脚本已按事件类型拆分：
  - `content` -> 聚合到 `data.answer`
  - `firstTextDelay/costMoney/totalTimeCost` -> 聚合到 `data.metrics`
  - 统计 `eventCount`
- 复测后，`answer` 已恢复为干净正文。

## 3. report-query/get-unread-list.py 返回过大

### 现象
- 请求参数：`pageSize=5`
- 平台实际返回：
  - `pageSize=100`
  - `size=100`

### 结论
- 这是平台接口行为与请求参数不一致，不是脚本组包错误。
- 脚本已正确发送 `{"pageIndex":1,"pageSize":5}`。
- 当前更像平台忽略或放大了分页大小。

### 已处理
- 脚本新增：
  - `--client-limit`
  - `--output-file`
- 现在可在不改平台行为的前提下控制终端输出。
- 默认只处理前 `200` 条；即使显式传更大值，脚本也最多只处理前 `500` 条。

## 4. report-message/find-my-new-msg-list.py 返回过大

### 现象
- 该接口不是分页接口。
- 实测 `data.total=186`，`msgList` 实际返回 169 条。

### 结论
- 这不是异常报错，而是接口设计本身返回“我的新消息汇总 + 明细列表”整包。
- 用户未读/新消息积压越多，返回越大。

### 已处理
- 脚本新增：
  - `--client-limit`
  - `--output-file`
- 默认只处理前 `200` 条；即使显式传更大值，脚本也最多只处理前 `500` 条。

## 5. todos/list-created-feedbacks.py 响应偏慢

### 现象
- 比普通 GET 接口耗时更长。
- 实测平台返回 17 条记录。

### 结论
- 当前没有证据表明脚本存在问题。
- 接口本身为全量返回、无分页，慢更可能来自平台检索与响应体大小。

### 已处理
- 脚本新增：
  - `--client-limit`
  - `--output-file`
- 默认只处理前 `200` 条；即使显式传更大值，脚本也最多只处理前 `500` 条。

## 当前仍属于平台侧待确认的问题

1. `/work-report/reportInfoOpenQuery/unreadList` 为什么忽略/放大 `pageSize`
2. `/work-report/template/listTemplates` 为什么空结果返回 `data=null` 而非标准空列表
3. `/work-report/todoTask/listCreatedFeedbacks` 是否支持服务端分页
