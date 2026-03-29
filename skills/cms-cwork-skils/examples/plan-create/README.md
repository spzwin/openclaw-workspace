# plan-create 示例

## 模块说明
创建高级工作任务，并指定汇报人、责任人等相关角色。

## 依赖脚本
`../../scripts/plan-create/create-simple.py`

## 对应接口
- `POST /work-report/open-platform/report/plan/create`

---

## 标准流程（含 3S1R 管理闭环）

### Step 1 — Suggest（建议）
**在创建任务之前，先给出建议方案。**

- 说明该接口用于创建高级工作任务，不是“发送汇报”
- 建议先确认 `reportEmpIdList`、`target`、`endTime` 等必填字段
- 提示创建后会直接生成任务与待办

```
建议：使用 create-simple 接口创建高级工作任务。
请先确认任务名称、任务目标、汇报人和结束时间。
该操作会直接创建任务，请确认相关参与人无误。
```

### Step 2 — Decide（确认/决策）
**涉及数据变动前（创建操作），必须获取用户明确决策。**

```
⚠️ 确认执行数据变动操作：
□ 任务名称：____
□ 任务要求：____
□ 任务目标：____
□ 汇报人 empId 列表：____
□ 结束时间（毫秒时间戳）：____
□ 输入 "确认提交" 以继续：____
```

### Step 3 — Execute（执行）
执行工作任务创建脚本。

### Step 4 — Log（留痕）
**数据变动结果必须完整记录。**

- 记录创建的任务标题、任务 ID、提交时间、操作人
- 格式：`[LOG] plan-create | planId:xxx | title:xxx | ts:ISO8601 | operator:user`

```
[LOG] plan-create | planId:1234567890 | title:开放平台测试-创建高级任务 | ts:2026-03-25T13:59:00+08:00 | operator:evan
```

---

## 输入格式

**Body：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `main` | string | 是 | 任务名称 |
| `needful` | string | 是 | 任务要求 |
| `target` | string | 是 | 任务目标 |
| `reportEmpIdList` | array | 是 | 汇报人 ID 列表 |
| `endTime` | number | 是 | 结束时间戳 |

---

## 输出格式

```json
{
  "resultCode": 1,
  "data": "2037896299117928449"
}
```

---

## 注意事项
- ⚠️ 该接口为写操作（POST），执行后会在服务器创建新记录
- 提交前必须经过完整的 Suggest → Decide → Log 闭环
- Log 必须包含任务 ID，供后续查询或追踪使用
- 该接口是“创建工作任务”，不是“发送汇报”，也不支持附件上传
