# 已安装技能清单

> 整理于 2026-02-28，方便在其他设备/环境快速复装。

---

## 1. 🧠 self-improving-agent

**功能：** AI 自我改进系统，让 agent 能从交互中学习、反思并优化自己的行为模式。

**安装命令：**
```bash
npx skills add charon-fan/agent-playbook@self-improving-agent -g -y
```

**来源：** https://skills.sh/charon-fan/agent-playbook/self-improving-agent  
**安装量：** 699+

---

## 2. 🔍 find-skills

**功能：** 技能发现工具，帮助 agent 搜索和安装新技能，连接 skills.sh 生态系统。

**安装命令：**
```bash
npx skills add vercel-labs/skills@find-skills -g -y
```

**来源：** https://skills.sh/vercel-labs/skills/find-skills  
**安装量：** 350k+

---

## 3. 🌐 agent-browser

**功能：** 给 agent 浏览器控制能力，可以打开网页、截图、点击交互等。

**安装命令：**
```bash
npx skills add vercel-labs/agent-browser@agent-browser -g -y
```

**来源：** https://skills.sh/vercel-labs/agent-browser/agent-browser  
**安装量：** 65k+

---

## 4. 🕸️ ontology

**功能：** 本体论知识图谱记忆系统。为 AI 提供结构化持久记忆，支持实体（Person、Project、Task、Event 等）的创建、查询和关联。数据存储在本地 `memory/ontology/graph.jsonl`。

**触发词：** "记住..."、"我知道什么关于X"、"把X和Y关联"、"显示X的依赖"

**安装命令（手动，不在 GitHub，来自 ClawHub）：**
```bash
curl -L "https://wry-manatee-359.convex.site/api/v1/download?slug=ontology" -o ontology-skill.zip
unzip ontology-skill.zip -d ontology-skill
mkdir -p ~/.agents/skills/ontology
cp -r ontology-skill/* ~/.agents/skills/ontology/
rm -rf ontology-skill ontology-skill.zip
```

**来源：** https://clawhub.ai/oswalpalash/ontology  
**版本：** v0.1.2

---

## 一键安装脚本（除 ontology 外）

```bash
npx skills add charon-fan/agent-playbook@self-improving-agent -g -y
npx skills add vercel-labs/skills@find-skills -g -y
npx skills add vercel-labs/agent-browser@agent-browser -g -y
```

## ontology 单独安装脚本

```bash
curl -L "https://wry-manatee-359.convex.site/api/v1/download?slug=ontology" -o ontology-skill.zip && \
unzip -o ontology-skill.zip -d ontology-skill && \
mkdir -p ~/.agents/skills/ontology && \
cp -r ontology-skill/* ~/.agents/skills/ontology/ && \
rm -rf ontology-skill ontology-skill.zip && \
ln -s ../../.agents/skills/ontology ~/.openclaw/skills/ontology && \
echo "ontology installed ✅"
```

> ⚠️ 注意：ontology 不在 GitHub/skills.sh，需手动下载并创建 symlink 到 `~/.openclaw/skills/`，才能让所有 agent 共享使用。
