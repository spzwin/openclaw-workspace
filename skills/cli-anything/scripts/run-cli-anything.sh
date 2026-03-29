#!/bin/bash
# run-cli-anything.sh - 通过 Claude Code 调用 CLI-Anything 插件
# 用法：./run-cli-anything.sh <软件路径或 GitHub URL>

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误：缺少参数${NC}"
    echo "用法：$0 <软件路径或 GitHub URL>"
    echo "示例："
    echo "  $0 ./gimp"
    echo "  $0 https://github.com/blender/blender"
    exit 1
fi

TARGET="$1"

# 检查 Claude Code 是否安装
if ! command -v claude &> /dev/null; then
    echo -e "${RED}错误：未找到 Claude Code${NC}"
    echo "请先安装：https://claude.ai/code"
    exit 1
fi

# 检查 CLI-Anything 插件是否可用
echo -e "${BLUE}检查 CLI-Anything 插件...${NC}"
if ! claude -p "/cli-anything --help" --print 2>&1 | grep -q "cli-anything"; then
    echo -e "${YELLOW}警告：CLI-Anything 插件可能未激活${NC}"
    echo "尝试运行：claude -p '/reload-plugins' --print"
    read -p "继续？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 开始执行
echo -e "${GREEN}开始为 '$TARGET' 生成 CLI...${NC}"
echo -e "${YELLOW}这可能需要 10-30 分钟，请耐心等待${NC}"
echo ""

# 使用 claude 非交互模式执行
claude -p "/cli-anything $TARGET" --print

echo ""
echo -e "${GREEN}完成！${NC}"
echo "生成的 CLI 将保存在目标目录的 agent-harness/ 文件夹中"
