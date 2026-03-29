# 调度中心核心模块

## 目录结构

```
orchestrator/
├── index.ts            # 主入口
├── notification.ts     # 通知处理
├── progress.ts         # 进度更新
├── dispatcher.ts       # 任务派发
└── session-manager.ts  # Session 管理
```

## 实现状态

- [ ] 通知处理器
- [ ] 进度更新器
- [ ] 任务派发器
- [ ] Session 管理器
- [ ] 文件锁工具
- [ ] 日志工具

## 下一步

1. 实现基础工具函数 (fs-utils.ts, logger.ts)
2. 实现 Session 管理器 (session-manager.ts)
3. 实现通知处理器 (notification.ts)
4. 实现任务派发器 (dispatcher.ts)
5. 集成测试
