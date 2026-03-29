# 查询任务树

**接口**: `GET /bp/task/v2/getSimpleTree`  
**描述**: 根据分组 ID 查询该分组下的完整 BP 任务树形结构（目标 → 关键成果 → 关键举措）

---

## 请求

**URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp/task/v2/getSimpleTree`

**Headers**:
```
appKey: <your-app-key>
```

**参数** (Query):

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| groupId | string | 是 | 分组 ID（来自 `4.2 获取分组树` 或 `4.3 批量查询` 返回） |

---

## 响应

**Schema**: `Result<List<TaskTreeVO>>`

| 字段 | 类型 | 描述 |
|-----|------|------|
| data | array | 任务树（递归结构） |
| resultCode | integer | 响应码 |
| resultMsg | string | 响应消息 |

### TaskTreeVO 字段

| 字段 | 类型 | 描述 |
|-----|------|------|
| id | string | 任务 ID |
| name | string | 任务名称 |
| groupId | string | 所属分组 ID |
| type | string | 类型：`目标` / `关键成果` / `关键举措` |
| children | array | 子节点列表（递归结构） |

**示例**:
```json
{
 "resultCode": 1,
 "resultMsg": null,
 "data": [
 {
 "id": "2014631829004374017",
 "name": "Q1 业绩目标",
 "groupId": "2014631829004374001",
 "type": "目标",
 "children": [
 {
 "id": "2014631829004374018",
 "name": "客户拜访量达到 50 家",
 "groupId": "2014631829004374001",
 "type": "关键成果",
 "children": [
 {
 "id": "2014631829004374019",
 "name": "每周拜访 5 家客户",
 "groupId": "2014631829004374001",
 "type": "关键举措",
 "children": []
 }
 ]
 }
 ]
 }
 ]
}
```

---

## 审计用途

**BP 结构完整性检查**（审计第一块）：
1. **结构完整性**：检查是否包含 Goal + KR + KI 三层结构
2. **层级关系**：验证目标→KR→KI 的挂载关系是否正确
3. **快速概览**：获取任务树简要信息，识别缺失层级

**审计流程**：
1. 调用本接口获取任务树概览
2. 检查 `type="目标"` 节点下是否有 `type="关键成果"` 子节点
3. 检查 `type="关键成果"` 节点下是否有 `type="关键举措"` 子节点
4. 如有缺失，记录为"结构不完整"问题
5. 对需要深入审计的任务，调用详情接口（4.5/4.6/4.7）

---

## 脚本映射

无脚本，直接调用 API。
