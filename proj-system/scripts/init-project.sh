#!/bin/bash
# 项目初始化脚本

set -e

PROJECT_ID=${1:-"PROJ-$(date +%Y%m%d-%H%M)"}
PROJECT_NAME=${2:-"示例项目"}

WORKSPACE_ROOT="/Users/spzhong/.openclaw/workspace/workspace"
TEMPLATE_DIR="/Users/spzhong/.openclaw/workspace/proj-system/templates/sample-project"
PROJECT_DIR="$WORKSPACE_ROOT/$PROJECT_ID"

echo "🚀 初始化项目：$PROJECT_ID"
echo "   名称：$PROJECT_NAME"
echo "   路径：$PROJECT_DIR"

# 1. 复制模板
echo "📁 复制项目模板..."
mkdir -p "$WORKSPACE_ROOT"
cp -r "$TEMPLATE_DIR" "$PROJECT_DIR"

# 2. 更新 meta.json
echo "📝 更新项目元数据..."
cat "$PROJECT_DIR/meta.json" | \
  sed "s/\"id\": \"PROJ-20260319-001\"/\"id\": \"$PROJECT_ID\"/" | \
  sed "s/\"name\": \"示例项目 - 智能客服系统\"/\"name\": \"$PROJECT_NAME\"/" \
  > "$PROJECT_DIR/meta.json.tmp"
mv "$PROJECT_DIR/meta.json.tmp" "$PROJECT_DIR/meta.json"

# 3. 更新 pipeline.json
echo "📋 更新 Pipeline..."
cat "$PROJECT_DIR/pipeline.json" | \
  sed "s/\"projectId\": \"PROJ-20260319-001\"/\"projectId\": \"$PROJECT_ID\"/" \
  > "$PROJECT_DIR/pipeline.json.tmp"
mv "$PROJECT_DIR/pipeline.json.tmp" "$PROJECT_DIR/pipeline.json"

# 4. 更新所有 agent-status.json
echo "🔄 更新 Agent 状态文件..."
for rt_dir in RT01_BD_Analysis RT02_Research_Analysis RT03_Mid_Review RT04_Final_Review; do
  if [ -d "$PROJECT_DIR/$rt_dir" ]; then
    cat "$PROJECT_DIR/$rt_dir/agent-status.json" | \
      sed "s/\"projectId\": \"PROJ-20260319-001\"/\"projectId\": \"$PROJECT_ID\"/" \
      > "$PROJECT_DIR/$rt_dir/agent-status.json.tmp"
    mv "$PROJECT_DIR/$rt_dir/agent-status.json.tmp" "$PROJECT_DIR/$rt_dir/agent-status.json"
  fi
done

# 5. 创建 history.log
echo "📜 创建历史日志..."
echo "{\"timestamp\":\"$(date -Iseconds)\",\"action\":\"project_initialized\",\"status\":\"in_progress\"}" > "$PROJECT_DIR/history.log"

# 6. 初始化 Agent 目录
echo "🤖 初始化 Agent 目录..."
AGENTS_DIR="/Users/spzhong/.openclaw/workspace/proj-system/agents"
mkdir -p "$AGENTS_DIR"

for expert_id in expert-bd expert-research expert-mid-review expert-final-review; do
  mkdir -p "$AGENTS_DIR/$expert_id/status"
  
  if [ ! -f "$AGENTS_DIR/$expert_id/status.json" ]; then
    echo "   创建 Agent 状态：$expert_id"
    cat > "$AGENTS_DIR/$expert_id/status.json" << EOF
{
  "expertId": "$expert_id",
  "agentId": "pending",
  "sessionKey": "pending",
  "currentTask": null,
  "taskHistory": [],
  "capabilities": [],
  "lastHeartbeat": "$(date -Iseconds)",
  "status": "idle",
  "updatedAt": "$(date -Iseconds)"
}
EOF
  fi
done

echo ""
echo "✅ 项目初始化完成！"
echo ""
echo "📁 项目目录：$PROJECT_DIR"
echo "📋 下一步："
echo "   1. 启动调度中心：cd proj-system && npm start"
echo "   2. 创建专家 Agent 配置文件"
echo "   3. 派发第一个任务（RT01/RT02）"
echo ""
