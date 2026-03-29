# CLI-Anything Skill 使用指南

## 快速开始

### 方式 1：直接使用脚本

```bash
cd ~/.openclaw/workspace/skills/cli-anything

# 为本地软件生成 CLI
./scripts/run-cli-anything.sh ./gimp

# 为 GitHub 仓库生成 CLI
./scripts/run-cli-anything.sh https://github.com/blender/blender
```

### 方式 2：在 OpenClaw 对话中使用

告诉小爪：
```
帮我为 GIMP 生成 CLI，源码在 ./gimp
```

我会自动调用 Claude Code 的 CLI-Anything 插件来执行。

### 方式 3：直接用 Claude Code

```bash
claude -p "/cli-anything ./gimp" --print
```

## 支持的软件

理论上支持**任何 GUI 软件**，已有成功案例：

| 软件 | 类型 | 状态 |
|------|------|------|
| GIMP | 图像编辑 | ✅ 已测试 |
| Blender | 3D 建模 | ✅ 已测试 |
| LibreOffice | 办公套件 | ✅ 已测试 |
| Inkscape | 矢量图形 | ✅ 已测试 |
| Kdenlive | 视频编辑 | ✅ 已测试 |
| Audacity | 音频编辑 | ✅ 已测试 |
| OBS Studio | 直播推流 | ✅ 已测试 |
| Shotcut | 视频编辑 | ✅ 已测试 |
| Draw.io | 流程图 | ✅ 已测试 |
| Zoom | 视频会议 | ✅ 已测试 |

## 生成的 CLI 功能

生成的 CLI 包含：

- **完整命令集**：覆盖软件的主要功能
- **JSON 输出**：`--json` 模式，Agent 友好
- **REPL 模式**：交互式使用
- **撤销/重做**：状态管理
- **测试套件**：单元测试 + E2E 测试

### 示例（GIMP）

```bash
# 安装后使用
cli-anything-gimp new --width 1920 --height 1080
cli-anything-gimp open image.png
cli-anything-gimp filter blur --radius 5
cli-anything-gimp export output.png --json
```

## 7 个阶段详解

| 阶段 | 耗时 | 说明 |
|------|------|------|
| Phase 0: Source Acquisition | 1-2 min | 克隆仓库或验证路径 |
| Phase 1: Codebase Analysis | 5-10 min | 分析源码结构 |
| Phase 2: Architecture Design | 3-5 min | 设计 CLI 架构 |
| Phase 3: Implementation | 10-20 min | 编写代码 |
| Phase 4: Test Planning | 2-3 min | 制定测试计划 |
| Phase 5: Test Implementation | 5-10 min | 编写测试 |
| Phase 6: Test Documentation | 3-5 min | 运行测试并记录 |
| Phase 7: PyPI Publishing | 可选 | 打包发布 |

**总耗时**：约 30-60 分钟（取决于软件复杂度）

## 输出目录结构

```
<software>/
├── agent-harness/
│   └── cli_anything/
│       └── <software>/
│           ├── core/        # 核心模块
│           ├── utils/       # 工具函数
│           ├── tests/       # 测试文件
│           └── __main__.py  # CLI 入口
├── setup.py                 # PyPI 打包配置
├── TEST.md                  # 测试文档
└── <SOFTWARE>.md            # 软件特定 SOP
```

## 常见问题

### Q: 需要自己写代码吗？
**A:** 不需要！全自动生成，你只需要提供软件源码路径。

### Q: 生成的 CLI 能用吗？
**A:** 能！包含完整测试套件，通过后才算完成。

### Q: 可以修改生成的代码吗？
**A:** 当然可以！代码完全归你，随便改。

### Q: 支持 Windows 吗？
**A:** 支持，但 Claude Code 需要 bash 环境（Git Bash 或 WSL）。

## 下一步

生成完成后：

1. **本地测试**：`pip install -e .`
2. **验证功能**：运行几个命令试试
3. **提交 PyPI**（可选）：`pip install build && python -m build`

---

**有问题找小爪** 🐾
