# RT01 - BD 初审任务工作区

## 任务信息
- **任务 ID:** RT01
- **任务名称:** BD 初审 - 商机分析与需求确认
- **负责 Agent:** expert-bd
- **状态:** pending

## 工作目录结构
```
RT01_BD_Analysis/
├── readme.md          # 本文件 - 任务状态和说明
├── agent-status.json  # Agent 实时状态
├── drafts/            # 草稿目录
├── research/          # 调研资料
└── deliverables/      # 最终产物
    └── bd_report.md   # BD 分析报告（完成后生成）
```

## 工作流程
1. **接收任务** - 调度中心派发任务到 expert-bd session
2. **更新状态** - Agent 更新 `agent-status.json` 为 `working`
3. **执行工作** - 调研、分析、撰写草稿
4. **提交成果** - 完成 `bd_report.md`，更新状态为 `completed`
5. **提交通知** - 发送通知到调度中心，触发下一步

## 当前进展
- [ ] 接收任务
- [ ] 开始工作
- [ ] 完成草稿
- [ ] 提交成果

## 日志
- 2026-03-19 08:00 - 任务目录创建
