# plugin-report 示例

## 模块说明
插件场景的聚合查询，覆盖最新待办、未读汇报，以及二者的合并结果。

## 依赖脚本
- 聚合列表：`../../scripts/plugin-report/get-list.py`
- 最新待办：`../../scripts/plugin-report/get-latest-list.py`
- 未读汇报：`../../scripts/plugin-report/get-unread-list.py`

## 对应接口
- `POST /work-report/plugin/report/list`
- `POST /work-report/plugin/report/latestList`
- `POST /work-report/plugin/report/unreadList`

---

## 标准流程（含 3S1R 管理闭环）

### Step 1 — Suggest（建议）
```
建议：插件场景优先使用 get-list 一次拿聚合结果。
如需单独分页某一类数据，再改用 latestList 或 unreadList。
lastUpdateTime 建议首次传 0，后续增量同步再带上上次时间戳。
```

### Step 2 — Decide（确认/决策）
```
请确认：
□ 查询模式：聚合 / 最新待办 / 未读汇报
□ pageIndex：____
□ pageSize：____
□ lastUpdateTime：0 / 自定义：____
```

### Step 3 — Execute（执行）
执行对应插件列表查询脚本。

### Step 4 — Log（留痕）
```
[LOG] plugin-report | mode:list | page:1 size:10 | ts:ISO8601
```

---

## 注意事项
- 这是插件聚合能力，不等同于收件箱或通用待办
- `lastUpdateTime` 用于增量刷新，首次可传 `0`
- 查询为只读操作

---

## 输出格式

**聚合列表 `get-list.py`：**
```json
{
  "resultCode": 1,
  "data": {
    "latestTodoList": {
      "total": 13,
      "hasNew": true,
      "list": [
        {
          "todoId": "2037896300162347009",
          "id": null,
          "main": "测试开头 20260328 任务联调",
          "writeEmpName": "宋培众"
        }
      ]
    },
    "unreadReportList": {
      "total": 276,
      "hasNew": true,
      "list": [
        {
          "id": "2037801532216434690",
          "main": "【BP审查通知】请确认您的个人BP审查报告及修改要求",
          "writeEmpName": "BP"
        }
      ]
    }
  }
}
```

**单列表 `get-latest-list.py` / `get-unread-list.py`：**
```json
{
  "resultCode": 1,
  "data": {
    "total": 13,
    "hasNew": true,
    "list": [
      {
        "todoId": "2037896300162347009",
        "id": null,
        "main": "测试开头 20260328 任务联调",
        "writeEmpName": "宋培众"
      }
    ]
  }
}
```
