---
name: cli-anything
description: 通过 Claude Code 调用 CLI-Anything 插件，为任意 GUI 软件生成 CLI 工具。支持分析源码、设计架构、实现代码、测试和打包。
---

# CLI-Anything Skill — 通过 Claude Code 生成 GUI 软件的 CLI

**当前版本**: v1.0

**核心能力**：
- 为任意 GUI 软件（GIMP、Blender、LibreOffice 等）生成完整的 CLI harness
- 全自动 7 个阶段：源码分析 → 架构设计 → 实现 → 测试 → 打包
- 通过 Claude Code 插件系统执行，无需本地安装

## 前置条件

1. **Claude Code 已安装**：`claude --version` 返回 2.x+
2. **CLI-Anything 插件已安装**：运行 `/cli-anything --help` 可识别

## 使用方法

### 基础用法

```bash
# 为本地软件生成 CLI
/cli-anything <软件路径>

# 为 GitHub 仓库生成 CLI
/cli-anything https://github.com/owner/repo
```

### 在 OpenClaw 中调用

```bash
# 使用 claude CLI 非交互模式
claude -p "/cli-anything <软件路径>" --print
```

## 7 个阶段（全自动）

| 阶段 | 名称 | 说明 |
|------|------|------|
| Phase 0 | Source Acquisition | 克隆仓库或验证本地路径 |
| Phase 1 | Codebase Analysis | 分析源码，映射 GUI 操作到 API |
| Phase 2 | CLI Architecture Design | 设计命令分组、状态模型、输出格式 |
| Phase 3 | Implementation | 实现 Click CLI，包含 REPL、JSON 输出 |
| Phase 4 | Test Planning | 创建 TEST.md 测试计划 |
| Phase 5 | Test Implementation | 编写单元测试和 E2E 测试 |
| Phase 6 | Test Documentation | 运行测试并记录结果 |
| Phase 7 | PyPI Publishing | 打包并发布到 PyPI（可选） |

## 输出结构

生成的 CLI 包含：
- `cli-anything-<software>` 可执行命令
- 支持 `--json` 输出模式（Agent 友好）
- 支持 REPL 交互模式
- 完整的测试套件

## 示例

### 为 GIMP 生成 CLI

```bash
claude -p "/cli-anything ./gimp" --print
```

### 为 Blender 生成 CLI

```bash
claude -p "/cli-anything https://github.com/blender/blender" --print
```

## 注意事项

1. **软件路径必须有效**：不能只用软件名（如 "gimp"），必须提供源码路径或仓库 URL
2. **需要 Python 3.10+**：生成的 CLI 基于 Click 框架
3. **首次运行较慢**：7 个阶段全自动，可能需要 10-30 分钟
4. **网络要求**：克隆仓库需要访问 GitHub

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| `cli-anything: command not found` | 确认 Claude Code 插件已安装并 reload |
| SSH 认证失败 | 使用 HTTPS URL 而非 SSH |
| 权限不足 | 确保有软件源码的读取权限 |
| Python 版本过低 | 升级到 Python 3.10+ |

## 相关文件

- `scripts/run-cli-anything.sh` - 自动化执行脚本
- `examples/` - 使用示例
- `references/HARNESS.md` - CLI-Anything 方法论

## 快速开始

1. 准备好目标软件的源码路径或 GitHub URL
2. 运行 `claude -p "/cli-anything <路径>" --print`
3. 等待 7 个阶段完成
4. 使用生成的 `cli-anything-<software>` 命令

---

**技能作者**: 小爪 🐾
**基于**: HKUDS/CLI-Anything
