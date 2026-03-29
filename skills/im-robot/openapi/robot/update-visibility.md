# 更新机器人可见性

**接口**: `POST /robot/visibility/update`  
**描述**: 更新机器人可见性（私有/公开/指定范围）

---

## 请求

**URL**: `https://cwork-api-test.xgjktech.com.cn/im/robot/visibility/update`

**Headers**:
```
access-token: <your-access-token>
Content-Type: application/json
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| robotId | integer | 否 | 机器人 ID |
| visibleType | integer | 否 | 可见性类型：0-私有，1-公开，2-指定范围 |

**参数** (Body):

| 字段 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| visibleRange | array | 否 | 可见范围列表（visibleType=2 时必传） |

### visibleRange 项结构

| 字段 | 类型 | 描述 |
|-----|------|------|
| targetId | string | 目标 ID |
| targetType | string | 目标类型：USER-人员，DEPT-部门 |

**请求示例**（设为公开）:
```
POST /robot/visibility/update?robotId=123456&visibleType=1
```

**请求示例**（设为指定范围可见）:
```
POST /robot/visibility/update?robotId=123456&visibleType=2
Content-Type: application/json

[
  {"targetId": "user_001", "targetType": "USER"},
  {"targetId": "dept_002", "targetType": "DEPT"}
]
```

---

## 响应

**Schema**: `Result<boolean>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | boolean | 更新结果（true/false） |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

**示例**:
```json
{
  "data": true,
  "resultCode": 200,
  "resultMsg": "success"
}
```

---

## 脚本映射

无脚本，直接调用 API。
