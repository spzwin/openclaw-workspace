# 获取分组树

**接口**: `GET /bp/group/getTree`  
**描述**: 根据周期 ID 获取该周期下的完整分组树形结构（组织分组 + 个人分组）

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/group/getTree`

**Headers**:
```
appKey: <your-app-key>
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| periodId | string | 是 | 周期 ID（来自 `4.1 查询周期列表` 返回的 `PeriodVO.id`） |
| onlyPersonal | boolean | 否 | 是否只查询个人分组，默认 `false` |

---

## 响应

**Schema**: `Result<List<GroupTreeVO>>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | array | 分组树（递归结构） |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### GroupTreeVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 分组 ID |
| name | string | 分组名称 |
| type | string | 分组类型：`org` = 组织节点，`personal` = 个人节点 |
| employeeId | string | 员工 ID（仅 `type = personal` 时有效） |
| parentId | string | 父节点 ID |
| levelNumber | string | 层级编码 |
| children | array | 子节点列表（递归结构） |

**示例**:
```json
{
 "resultCode": 1,
 "resultMsg": null,
 "data": [
 {
 "id": "2014631829004371001",
 "name": "技术中心",
 "type": "org",
 "employeeId": null,
 "parentId": null,
 "levelNumber": "1",
 "children": [
 {
 "id": "2014631829004371002",
 "name": "张三",
 "type": "personal",
 "employeeId": "1234567890123456789",
 "parentId": "2014631829004371001",
 "levelNumber": "1.1",
 "children": []
 }
 ]
 }
 ]
}
```

---

## 审计用途

**组织审计范围定位**：
- `type = "org"`：组织分组（部门），用于审计部门级 BP
- `type = "personal"`：个人分组（员工），用于审计个人 BP

**审计场景**：
1. **部门审计**：遍历 `type="org"` 节点，获取部门下所有员工
2. **全员审计**：设置 `onlyPersonal=true`，只获取个人分组节点
3. **层级分析**：通过 `levelNumber` 分析组织层级结构

---

## 脚本映射

无脚本，直接调用 API。
