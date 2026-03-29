#!/usr/bin/env python3
# huiji-meeting-skill 统一入口（仅聚焦实时会议：列表、进行中、实时问答、总结、待办）

import os
import sys
from pathlib import Path

# 兼容 Windows 控制台编码：避免 print() 输出中文/emoji 时因 GBK(cp936) 报 UnicodeEncodeError
if os.name == "nt":
    # 仅做 best-effort；不同 Windows/Python 环境能力不完全一致
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 项目根目录
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.client import MeetingClient
from src.intent import IntentManager, search_meetings
from src.ai_qa import AIQA
from src.ai_provider import AIProvider
from src.formatter import format_meeting_list, format_in_progress_helper, format_search_results


def get_client(app_key: str | None = None) -> MeetingClient:
    """获取会议客户端。AppKey 读取顺序见 common/auth.md：环境变量 → 上下文传入 → 配置文件。"""
    key = app_key or os.environ.get("XG_BIZ_API_KEY", "")
    return MeetingClient(app_key=key or None)


def list_meetings(count: int = 10, force_refresh: bool = False) -> dict:
    """获取最近 N 条会议。"""
    if count > 20:
        count = 20
    client = get_client()
    result = client.get_meetings(page_num=0, page_size=count, force_refresh=force_refresh)
    return result


def in_progress_meetings() -> list:
    """获取进行中的会议。"""
    client = get_client()
    return client.get_in_progress_meetings(force_refresh=True)


def understand_query(query: str) -> dict:
    """意图理解并返回会议列表结果。"""
    return IntentManager().understand(query)


def real_time_helper_text() -> str:
    """返回实时会议助手说明 + 进行中会议列表。"""
    client = get_client()
    in_progress = client.get_in_progress_meetings(force_refresh=True)
    return format_in_progress_helper(in_progress)


def search(keyword: str) -> list:
    """关键词搜索会议。"""
    client = get_client()
    return search_meetings(client, keyword)


def get_meeting_content(meeting_id: str, is_in_progress: bool | None = None) -> str:
    """获取会议完整转写内容（同步）。已知为进行中时可传 is_in_progress=True 仅用 splitRecordList。"""
    qa = AIQA(get_client())
    full = qa.get_full_meeting_content_sync(meeting_id, is_in_progress=is_in_progress)
    return full.get("content", "")


def answer_question(meeting_id: str, question: str, is_in_progress: bool | None = None) -> str:
    """实时问答：生成提示词或说明（实际 AI 回答由调用方或 agent 完成）。进行中会议传 is_in_progress=True。"""
    qa = AIQA(get_client())
    return qa.handle_question(meeting_id, question, is_in_progress=is_in_progress)


def summarize_meeting(
    meeting_id: str, content: str | None = None, is_in_progress: bool | None = None
) -> str | dict:
    """生成会议总结报告。若未传 content 则先按状态拉取。
    当内容来自 reportInfo 的 data.textReport 时，已是慧记侧大模型生成的结构化 Markdown 报告，直接返回，不再经本 skill 大模型二次总结或格式优化。"""
    client = get_client()
    if not content:
        qa = AIQA(client)
        full = qa.get_full_meeting_content_sync(meeting_id, is_in_progress=is_in_progress)
        content = full.get("content", "")
        source = full.get("source", "")
        if source == "reportInfo" and content:
            return content.strip()
    if len(content) < 100:
        return "会议内容过少，无法生成有效报告。"
    provider = AIProvider()
    result = provider.generate_meeting_report(content)
    if isinstance(result, dict) and result.get("fallback"):
        return result
    return result


def extract_todos(
    meeting_id: str, content: str | None = None, is_in_progress: bool | None = None
) -> str | dict:
    """提取待办事项。未传 content 时按状态拉取（进行中仅用 splitRecordList）。"""
    client = get_client()
    if not content:
        qa = AIQA(client)
        full = qa.get_full_meeting_content_sync(meeting_id, is_in_progress=is_in_progress)
        content = full.get("content", "")
    if not content:
        return "暂无会议内容可提取待办。"
    provider = AIProvider()
    result = provider.generate_todo_list(content)
    if isinstance(result, dict) and result.get("fallback"):
        return result
    return result


if __name__ == "__main__":
    # 简单 CLI 演示
    import json
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        r = list_meetings(n, force_refresh=True)
        print(format_meeting_list(r["meetings"], f"最近 {n} 条会议记录", n))
    elif cmd == "in_progress":
        m = in_progress_meetings()
        print(format_in_progress_helper(m))
    elif cmd == "query" and len(sys.argv) > 2:
        q = " ".join(sys.argv[2:])
        r = understand_query(q)
        print(format_meeting_list(r["meetings"], r["title"]))
    else:
        print("用法: python main.py list [N] | in_progress | query <用户问题>")
