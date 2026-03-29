# 查询周期列表

**接口**: `GET /bp/period/getAllPeriod`  
**描述**: 获取系统中所有 BP 周期信息，通常作为审计流程的**第一步**

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/period/getAllPeriod`

**Headers**:
```
appKey: <your-app-key>
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| name | string | 否 | 周期名称，支持模糊搜索（如 "2026"） |

---

## 响应

**Schema**: `Result<List<PeriodVO>>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | array | 周期列表 |
| resultCode | integer | 响应码（1=成功） |
| resultMsg | string | 响应消息 |

### PeriodVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 周期 ID |
| name | string | 周期名称 |
| status | integer | 周期状态：`1` = 启用，`0` = 未启用 |

**示例**:
```json
{
 "resultCode": 1,
 "resultMsg": null,
 "data": [
 {
 "id": "2014631829004370001",
 "name": "2026 年 Q1",
 "status": 1
 },
 {
 "id": "2014631829004370002",
 "name": "2026 年 Q2",
 "status": 0
 }
 ]
}
```

---

## 审计用途

**审计流程第一步**：获取启用周期的 `periodId`，用于后续：
- 调用 `4.2 获取分组树` 的 `periodId` 入参
- 调用 `4.12 按名称模糊搜索分组` 的 `periodId` 入参

**注意**：通常选择 `status = 1`（启用状态）的周期进行审计。

---

## 脚本映射

无脚本，直接调用 API。
