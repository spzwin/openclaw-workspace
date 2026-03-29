# report-message 示例

## 模块说明
覆盖我的新消息查询，以及阅读汇报后清理未读/新消息提醒的状态变更能力。

## 依赖脚本
- 我的新消息：`../../scripts/report-message/find-my-new-msg-list.py`
- 阅读汇报：`../../scripts/report-message/read-report.py`

## 对应接口
- `GET /work-report/open-platform/report/findMyNewMsgList`
- `GET /work-report/open-platform/report/readReport`

---

## 标准流程（含 3S1R 管理闭环）

### 场景一：查询我的新消息

#### Step 1 — Suggest（建议）
```
建议：默认查询重要消息（msgType=1）。
如需按其他业务消息类型过滤，再显式传入 msgType。
```

#### Step 2 — Decide（确认/决策）
```
请确认：
□ msgType：默认 1 / 自定义：____
```

#### Step 3 — Execute（执行）
执行新消息查询脚本。

#### Step 4 — Log（留痕）
```
[LOG] report-message.findMyNewMsgList | msgType:1 | ts:ISO8601
```

### 场景二：阅读汇报并清理提醒（数据变动操作 ⚠️）

#### Step 1 — Suggest（建议）
**涉及状态变更前，必须先说明副作用。**

```
建议：只有在确认用户确实要将该汇报标记为已读时，才调用 readReport。
该操作会清除当前用户下该汇报的未读和新消息提醒。
```

#### Step 2 — Decide（确认/决策）
**数据变动前，必须获取用户明确决策。**

```
⚠️ 确认执行阅读汇报：
□ reportId：____
□ 影响：标记已读并清除提醒
□ 输入 "确认已读" 以继续：____
```

#### Step 3 — Execute（执行）
执行阅读汇报脚本。

#### Step 4 — Log（留痕）
```
[LOG] report-message.readReport | reportId:xxx | action:mark-read | ts:ISO8601 | operator:user
```

---

## 注意事项
- `findMyNewMsgList` 为只读查询
- `readReport` 为状态变更操作，必须走 Suggest → Decide → Execute → Log
- `readReport` 使用 `GET`，但语义上不是只读接口

---

## 输出格式

**我的新消息：**
```json
{
  "resultCode": 1,
  "data": {
    "total": 186,
    "msgList": [
      {
        "unReadCount": 1,
        "reportId": "2037801532216434690",
        "reportTitle": "【BP审查通知】请确认您的个人BP审查报告及修改要求",
        "lastReplyTime": "2026-03-28 15:58:40",
        "replyEmployeeName": "BP",
        "type": "汇报提交通知"
      }
    ],
    "serverReturnedSize": 169,
    "clientLimit": 3,
    "clientReturnedSize": 3
  }
}
```

**阅读汇报：**
```json
{
  "resultCode": 1,
  "data": true
}
```

补充说明：
- `find-my-new-msg-list.py` 默认只处理前 `200` 条，最大只处理前 `500` 条
- `read-report.py` 有真实副作用：会清理当前用户的未读和新消息提醒
