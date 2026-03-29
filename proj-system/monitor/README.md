# 🐾 Agent 监控中心

本地 Web 监控页面，实时查看各 Agent 工作状态和项目产出。

## 启动方式

```bash
cd /Users/spzhong/.openclaw/workspace/proj-system/monitor
node server.js
```

## 访问地址

打开浏览器访问：**http://localhost:3456**

## 功能

- ✅ 左侧显示所有项目列表（ID + 名称 + 状态）
- ✅ 右侧显示选中项目的详细信息
- ✅ 实时展示各 Agent 状态（空闲/工作中/错误）
- ✅ 显示项目交付产物列表
- ✅ 每 5 秒自动刷新

## 监控的 Agent

- orchestrator（任务调度）
- expert-research（初审创研）
- expert-bd（初审 BD）
- expert-mid-review（中评）
- expert-final-review（终评）

## 数据来源

- 项目信息：`workspace/{project-id}/project.json`
- Agent 状态：`agents/{agent-id}/status.json`
- 交付产物：项目目录下的 `.md` 和 `.json` 文件

## 停止服务

按 `Ctrl+C` 终止
