# 机器人模块使用示例

**模块**: `robot`  
**目标用户**: AI Agent

---

## 触发条件

当用户请求涉及以下场景时，使用本模块：

- **注册机器人**: "帮我注册一个机器人"、"创建一个私人助理"
- **查询列表**: "我有哪些机器人"、"查看机器人列表"
- **删除机器人**: "删除这个机器人"、"移除 agentId 为 main 的机器人"
- **设置可见性**: "把这个机器人设为公开"、"限制只有特定人员可见"
- **快捷指令**: "执行重置指令"、"有哪些可用指令"

---

## 标准流程

### 场景 1: 注册私有机器人

```
1. 调用 POST /robot/private/register
   请求：{"agentId": "main", "name": "我的私人助理"}

2. 解析响应，获取 appKey、baseUrl、wsBaseUrl

3. 保存配置，用于后续连接
```

### 场景 2: 查看机器人列表

```
1. 调用 GET /robot/list

2. 解析响应 data 数组

3. 展示关键字段：name、agentId、isOnline、visibleType、lastUseTime
```

### 场景 3: 删除机器人

```
1. 确认要删除的 agentId

2. 调用 POST /robot/deleteMyRobot?agentId=<agentId>

3. 检查响应 data 是否为 true
```

### 场景 4: 更新可见性

```
1. 确定目标 robotId 和 visibleType

2. 如 visibleType=2，准备 visibleRange 数组

3. 调用 POST /robot/visibility/update

4. 检查响应确认更新成功
```

### 场景 5: 执行快捷指令

```
1. （可选）调用 GET /robot/shortcut/list 获取可用指令

2. 调用 POST /robot/shortcut/execute
   请求：{"command": "RESET", "groupId": "group_xxx"}

3. 检查响应 data 确认执行结果
```

---

## 注意事项

1. **认证前置**: 所有接口需要先获取 access-token（见 `../../common/auth.md`）
2. **visibleType=2**: 指定范围可见时，visibleRange 必填
3. **agentId 唯一性**: 同一个 agentId 不能重复注册
4. **响应处理**: 统一检查 resultCode 和 resultMsg 判断是否成功
