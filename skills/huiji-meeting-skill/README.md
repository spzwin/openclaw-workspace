# huiji-meeting-skill（Python 版）

AI 慧记**实时会议**技能：会议列表、进行中识别、实时问答、总结报告、待办提取。仅聚焦实时会议能力，格式与鉴权规范对齐 **skill-template**（common/auth、openapi、examples）。

## 结构

```
huiji-meeting-skill/
├── SKILL.md           # Agent 能力索引、路由表、输出与提示词
├── common/
│   ├── auth.md        # 鉴权与 AppKey 读取顺序（与 skill-template 一致）
│   └── conventions.md # 通用约束
├── openapi/
│   ├── common/
│   │   └── appkey.md  # AppKey 使用（慧记会议 API）
│   └── meeting/       # 会议列表、分片转写
├── examples/
│   └── meeting/       # 使用说明与流程
├── README.md
├── requirements.txt
├── main.py            # 统一入口与 CLI
├── config/
│   └── default.json
└── src/               # 实现（client / intent / ai_qa / formatter 等）
```

## 环境

- Python 3.10+
- **鉴权**：AppKey 读取顺序见 **`common/auth.md`**（环境变量 `XG_BIZ_API_KEY` → 上下文 → 用户提供）；接口使用见 `openapi/common/appkey.md`。

```bash
pip install -r requirements.txt
```

## 配置

`config/default.json` 中可配置：

- `apiBaseUrl`：会议列表接口
- `appKey`：可选；**环境变量 `XG_BIZ_API_KEY` 优先**（与 common/auth.md 一致）
- `cache.ttl` / `cache.maxSize`
- `monitor` / `notification`：监控与通知（可选）

**大模型（可选）**：`summarize_meeting`、`extract_todos` 在内容来自转写（非 reportInfo）时会调用 LLM 生成报告/待办。可设置环境变量 `OPENAI_API_KEY` 并安装 `pip install openai`；不配置时返回说明文案，不报错。

## 使用示例

```python
from main import (
    list_meetings,
    in_progress_meetings,
    understand_query,
    real_time_helper_text,
    search,
    answer_question,
    summarize_meeting,
    extract_todos,
)

# 最近 N 条
r = list_meetings(5)

# 进行中
m = in_progress_meetings()

# 意图理解
r = understand_query("帮我找最近 4 条记录")

# 实时助手文案
text = real_time_helper_text()

# 搜索
meetings = search("OpenClaw")

# 实时问答（返回提示词说明，实际回答由 Agent/AI 完成）
msg = answer_question(meeting_id, "最近 10 分钟讲了什么？")

# 总结与待办
report = summarize_meeting(meeting_id)
todos = extract_todos(meeting_id)
```

CLI：

```bash
python main.py list 5          # 最近 5 条
python main.py in_progress     # 进行中
python main.py query 最近4条记录
```

## 功能说明

详见 **SKILL.md**：输出规范、时间范围理解、报告/待办提示词等。

