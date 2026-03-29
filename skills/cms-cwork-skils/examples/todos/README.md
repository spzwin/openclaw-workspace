# todos 示例

## 模块说明
待办事项管理，支持待办列表查询、创建的反馈待办查询，以及建议/决策类待办完成。

## 依赖脚本
- 列表：`../../scripts/todos/get-list.py`
- 我创建的反馈待办：`../../scripts/todos/list-created-feedbacks.py`
- 完成：`../../scripts/todos/complete.py`

## 对应接口
- `POST /work-report/todoTask/todoList`
- `GET /work-report/todoTask/listCreatedFeedbacks`
- `POST /work-report/open-platform/todo/completeTodo`

---

## 标准流程（含 3S1R 管理闭环）

### 场景一：查询待办列表

#### Step 1 — Suggest（建议）
```
建议：默认拉取当前用户的所有待办事项。
如需筛选类型，可补充 type 参数（plan/sign/lead/feedback/file_audit）。
```

#### Step 2 — Decide（确认/决策）
```
请确认：
□ 查询范围：全部 / 指定 type：____
□ 是否需要 executionResult：是 / 否
```

#### Step 3 — Execute（执行）
执行待办列表查询。

#### Step 4 — Log（留痕）
```
[LOG] todos.list | type:feedback | result:N | ts:ISO8601
```

---

### 场景二：完成待办项（数据变动操作 ⚠️）

#### Step 1 — Suggest（建议）
**涉及数据变动前，必须先给出建议并说明影响。**

```
建议：对待办项 [todoId] 提交建议或决策内容。
如果是决策类待办，需要额外提供 operate=agree/disagree。
注意：该操作会真正完成待办，必须经过明确确认。
```

#### Step 2 — Decide（确认/决策）
**数据变动前，必须获取用户明确决策。**

```
⚠️ 确认执行数据变动操作：
□ 待办项 ID：____
□ 处理内容 content：____
□ operate（决策类可选）：agree / disagree / 不传
□ 输入 "确认" 以继续：____
```

#### Step 3 — Execute（执行）
执行完成操作脚本。

#### Step 4 — Log（留痕）
**数据变动结果必须完整记录。**

```
[LOG] todos.complete | todoId:xxx | action:complete | ts:ISO8601 | operator:user
```

---

## 输出格式

**列表查询：**
```json
{
  "resultCode": 1,
  "data": {
    "list": []
  }
}
```

**完成操作：**
```json
{
  "resultCode": 1,
  "data": true
}
```

---

## 注意事项
- 查询操作：只读，日志记录参数
- `listCreatedFeedbacks` 查询的是“我创建的反馈待办”，不是当前待处理待办池
- 完成操作：数据变动，需强制 Suggest → Decide → Log 闭环
- 日志必须包含操作类型（query/complete）、操作时间、操作人
