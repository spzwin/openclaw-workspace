# 批量查询员工分组 ID

**接口**: `POST /bp/group/getPersonalGroupIds`  
**描述**: 根据员工 ID 列表，快速获取每个员工在当前启用周期下的个人分组 ID

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/group/getPersonalGroupIds`

**Headers**:
```
appKey: <your-app-key>
Content-Type: application/json
```

**参数** (Body):

请求体为 JSON 数组，元素为员工 ID（string 类型）：
```json
["1234567890123456789", "1234567890123456790", "1234567890123456791"]
```

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| (body) | array | 是 | 员工 ID 列表 |

---

## 响应

**Schema**: `Result<Map<string, string>>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | object | Map 结构，key=员工 ID，value=分组 ID |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

**响应示例**:
```json
{
 "resultCode": 1,
 "resultMsg": null,
 "data": {
 "1234567890123456789": "2014631829004374001",
 "1234567890123456790": null,
 "1234567890123456791": "2014631829004374003"
 }
}
```

**说明**：若 value 为 `null`，说明该员工在当前周期未创建 BP。

---

## 审计用途

**快速定位员工 BP**：
- 批量获取员工分组 ID，无需先查周期再查分组树
- 识别哪些员工未创建 BP（value=null）

**审计场景**：
1. **覆盖率分析**：统计部门内有多少员工创建了 BP
2. **快速审计**：已知员工 ID 列表，快速获取其 BP 数据进行审计
3. **缺失识别**：识别未创建 BP 的员工，纳入审计问题清单

---

## 脚本映射

无脚本，直接调用 API。
