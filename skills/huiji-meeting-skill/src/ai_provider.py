# 会议报告与待办提取：调用大模型生成内容（可配置 LLM）
import os
from typing import Any, Optional

from .prompts import REPORT_SYSTEM_PROMPT, TODO_EXTRACT_PROMPT

# 未配置 LLM 时返回给 Agent 的结构：调用方可根据 fallback 自行生成报告/待办
FALLBACK_TASK_REPORT = "meeting_report"
FALLBACK_TASK_TODO = "todo_extract"


def _call_llm(system_prompt: str, user_content: str, max_tokens: int = 4096) -> Optional[str]:
    """若已配置 OPENAI_API_KEY 且可用的 openai 库存在，则调用；否则返回 None。"""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY_BASE64")
    if not api_key:
        return None
    try:
        import openai
    except ImportError:
        return None
    client = getattr(openai, "OpenAI", None)
    if not client:
        return None
    try:
        c = client(api_key=api_key)
        # 兼容 openai>=1.0 的 chat.completions.create
        resp = c.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=max_tokens,
        )
        if resp.choices and len(resp.choices) > 0:
            return (resp.choices[0].message.content or "").strip()
    except Exception:
        pass
    return None


def _fallback_dict(task: str, system_prompt: str, content: str) -> dict[str, Any]:
    """未配置或调用失败时返回结构化数据，供 Agent 自行生成报告/待办。"""
    return {
        "fallback": True,
        "task": task,
        "content": content,
        "system_prompt": system_prompt,
    }


class AIProvider:
    """会议报告生成与待办提取，依赖大模型。默认尝试 OpenAI 兼容接口；未配置时返回 dict 供 Agent 使用。"""

    def generate_meeting_report(self, content: str) -> str | dict[str, Any]:
        """根据会议原文生成结构化会议报告（Markdown）。未配置 LLM 时返回 dict 供 Agent 自行总结。"""
        if not content or len(content.strip()) < 100:
            return "会议内容过少，无法生成有效报告。"
        out = _call_llm(REPORT_SYSTEM_PROMPT, content)
        if out:
            return out
        return _fallback_dict(FALLBACK_TASK_REPORT, REPORT_SYSTEM_PROMPT, content)

    def generate_todo_list(self, content: str) -> str | dict[str, Any]:
        """从会议内容中提取待办事项。未配置 LLM 时返回 dict 供 Agent 自行提取。"""
        if not content or len(content.strip()) < 100:
            return "会议内容过少，无法提取待办。"
        out = _call_llm(TODO_EXTRACT_PROMPT, content, max_tokens=2048)
        if out:
            return out
        return _fallback_dict(FALLBACK_TASK_TODO, TODO_EXTRACT_PROMPT, content)
