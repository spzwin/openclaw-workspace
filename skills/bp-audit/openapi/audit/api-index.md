# 审计模块 API 索引

**模块**: `audit`  
**基础路径**: `/open-api/bp`  
**域名**: `cwork-web-test.xgjktech.com.cn`  
**完整 URL**: `https://cwork-web-test.xgjktech.com.cn/open-api/bp`

---

## 接口清单

| 接口 | 方法 | 路径 | 描述 | 文档 |
|-----|------|------|------|------|
| 查询周期列表 | GET | `/bp/period/getAllPeriod` | 获取所有 BP 周期，筛选启用周期 | [`get-periods.md`](./get-periods.md) |
| 获取分组树 | GET | `/bp/group/getTree` | 获取周期下的完整分组树形结构 | [`get-group-tree.md`](./get-group-tree.md) |
| 批量查询员工分组 | POST | `/bp/group/getPersonalGroupIds` | 根据员工 ID 获取个人分组 ID | [`get-employee-groups.md`](./get-employee-groups.md) |
| 查询任务树 | GET | `/bp/task/v2/getSimpleTree` | 获取分组下的任务树（目标→KR→KI） | [`get-task-tree.md`](./get-task-tree.md) |
| 获取目标详情 | GET | `/bp/task/v2/getGoalAndKeyResult` | 获取目标及下所有 KR 和 KI | [`get-goal-detail.md`](./get-goal-detail.md) |
| 获取 KR 详情 | GET | `/bp/task/v2/getKeyResult` | 获取关键成果及下所有 KI | [`get-kr-detail.md`](./get-kr-detail.md) |
| 获取 KI 详情 | GET | `/bp/task/v2/getAction` | 获取关键举措详情 | [`get-action-detail.md`](./get-action-detail.md) |
| 分页查询汇报 | POST | `/bp/task/relation/pageAllReports` | 查询任务关联的汇报记录 | [`get-reports.md`](./get-reports.md) |
| 搜索任务/分组 | GET | `/bp/task/v2/searchByName` | 按名称模糊搜索任务 | [`search.md`](./search.md) |
| 搜索分组 | GET | `/bp/group/searchByName` | 按名称模糊搜索分组 | [`search.md`](./search.md) |

---

## 认证要求

所有接口需要在 Header 中携带：
```
appKey: <your-app-key>
```

详见 [`../../common/auth.md`](../../common/auth.md)

---

## 模块说明

本模块提供 AI Agent 审计 BP 目标所需的完整能力：
- **数据获取**：周期、分组、任务树、详情、汇报
- **审计分析**：合规性检查、上下承接对齐、GAP 分析
- **搜索定位**：按名称快速定位任务/分组

---

## 审计数据流向

```
1. 查询周期列表 → 获取 periodId（status=1）
       ↓
2. 获取分组树 → 获取 groupId（org 或 personal）
       ↓
3. 查询任务树 → 获取任务 id（目标/KR/KI）
       ↓
4. 获取详情 → 获取完整数据（含 upwardTaskList/downTaskList）
       ↓
5. 执行审计 → 输出审计报告
```
