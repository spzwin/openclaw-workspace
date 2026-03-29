# 输出格式化 - 列表/搜索等格式（与 SKILL.md 一致）
from datetime import datetime, timedelta, timezone
from typing import Any

_CN_TZ = timezone(timedelta(hours=8))


def _format_time_zh(iso_time: str | None) -> str:
    if not iso_time:
        return "(无)"
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        # API 侧 ISO 基于 UTC（Z 后缀），这里统一换算为北京时间 UTC+8 再展示
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(_CN_TZ)
        return dt.strftime("%Y/%m/%d %H:%M:%S")
    except Exception:
        return iso_time


def _duration_str(ms: int | None) -> str:
    if ms is None or ms <= 0:
        return ""
    s = ms // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}小时{m}分{s}秒"
    return f"{m}分{s}秒"


def _span_ms_from_meeting(meeting: dict) -> int | None:
    """从 create_time / finish_time 的 ISO 字符串计算时间跨度（毫秒）。"""
    ct = meeting.get("create_time")
    ft = meeting.get("finish_time")
    if not ct or not ft:
        return None
    try:
        t1 = datetime.fromisoformat(ct.replace("Z", "+00:00")).timestamp() * 1000
        t2 = datetime.fromisoformat(ft.replace("Z", "+00:00")).timestamp() * 1000
        return int(t2 - t1)
    except Exception:
        return None


def _duration_block_for_meeting(meeting: dict) -> list[str]:
    """已完成会议的时长与结束时间行：有 meetingLength 时以它为准并做合理性校验；无则用时间跨度。返回要追加的若干行。"""
    lines: list[str] = []
    length_ms = meeting.get("meeting_length")
    span_ms = _span_ms_from_meeting(meeting)
    ft = meeting.get("finish_time")
    show_finish_time = True

    if length_ms and length_ms > 0:
        duration_str = _duration_str(length_ms)
        if span_ms is not None and length_ms > 0:
            diff_ratio = abs(span_ms - length_ms) / length_ms
            if diff_ratio > 0.2:
                duration_str += "（含暂停）"
            if span_ms > 10 * length_ms:
                show_finish_time = False
        lines.append(f"⏱️ **时长:** {duration_str}<br>")
    else:
        if span_ms is not None and span_ms > 0:
            lines.append(f"⏱️ **时长:** {_duration_str(span_ms)}<br>")
        else:
            lines.append("⏱️ **时长:** (未知)<br>")

    if show_finish_time and ft:
        lines.append(f"✅ **结束时间:** {_format_time_zh(ft)}<br>")
    return lines


def _brief_from_meeting(meeting: dict) -> str:
    """从 tidyText 或 simpleSummary 提取简介，最多约 280 字。"""
    tidy = meeting.get("tidy_text") or ""
    summary = meeting.get("summary") or ""
    if tidy:
        # tidyText 格式: **00:00:00 主题** 正文。取所有主题段正文，每段前80字，最多4段
        parts = []
        for segment in tidy.replace("**", "\n").split("\n"):
            segment = segment.strip()
            if not segment or segment[0].isdigit() and ":" in segment[:10]:
                continue
            parts.append(segment[:80])
        text = "；".join(parts[:4])
        return (text[:280] + "…") if len(text) > 280 else text
    if summary:
        return (summary[:280] + "…") if len(summary) > 280 else summary
    return "(暂无)"


def _keywords_from_meeting(meeting: dict) -> str:
    kw_list = meeting.get("keyword_list") or []
    if isinstance(kw_list, list):
        keywords = [k.get("keyword", k) if isinstance(k, dict) else k for k in kw_list[:5]]
        return ", ".join(str(k) for k in keywords if k)
    return "(无)"


def format_meeting_list(meetings: list[dict], title: str, max_items: int = 10) -> str:
    """列表模式：最近 N 条会议记录。"""
    lines = [f"### 📋 {title}", ""]
    if not meetings:
        lines.extend(
            [
                "当前列表中没有匹配到会议记录。",
                "",
                "---",
                "💡 **建议**：如果您记得会议标题里的关键词，可以这样搜索：",
                "- 🔍 搜索会议标题: \"搜索 关键词\" 或 \"找找关于 关键词 的会议\"",
                "",
            ]
        )
        return "\n".join(lines)
    for m in meetings[:max_items]:
        name = m.get("name") or "(无标题)"
        create_time = _format_time_zh(m.get("create_time"))
        status = m.get("status_text") or "未知"
        brief = _brief_from_meeting(m)
        keywords = _keywords_from_meeting(m)
        block = [
            "---",
            f"**会议名称:** {name}<br>",
            f"📅 **创建时间:** {create_time}<br>",
            f"📊 **状态:** {status}<br>",
        ]
        if m.get("status") == "completed":
            block.extend(_duration_block_for_meeting(m))
        block.extend(
            [
                f"📝 **简介:** {brief}<br>",
                f"🔑 **标签:** {keywords}<br>",
                "---",
                "",
            ]
        )
        lines.extend(block)
    return "\n".join(lines)


def format_search_results(meetings: list[dict], keyword: str, context_snippet: dict[str, str] | None = None) -> str:
    """搜索模式：关键词搜索结果。"""
    n = len(meetings)
    lines = [f'### 🔍 搜索结果: "{keyword}" (找到 {n} 条)', ""]
    for m in meetings[:10]:
        name = m.get("name") or "(无标题)"
        create_time = _format_time_zh(m.get("create_time"))
        status = m.get("status_text") or "未知"
        keywords = _keywords_from_meeting(m)
        mid = m.get("_id") or m.get("meeting_id") or ""
        snippet = (context_snippet or {}).get(mid, _brief_from_meeting(m))
        if len(snippet) > 100:
            snippet = snippet[:100] + "…"
        block = [
            "---",
            f"**会议名称:** {name}<br>",
            f"📅 **创建时间:** {create_time}<br>",
            f"📊 **状态:** {status}<br>",
            f"🔑 **匹配标签:** {keywords}<br>",
            f"📝 **相关内容:** {snippet}<br>",
            "---",
            "",
        ]
        lines.extend(block)
    return "\n".join(lines)


def format_in_progress_helper(in_progress: list[dict]) -> str:
    """实时会议助手：进行中会议列表（当天且未结束），多条时优先推荐最新的一条。"""
    lines = ["### 🎙️ 实时会议助手", ""]
    n = len(in_progress)
    if n == 0:
        lines.append("当前没有当天的进行中会议。")
        lines.append("")
        lines.extend([
            "---",
            "💡 **您可以：**",
            "",
            "📋 查看最近会议: \"最近 5 条会议\"<br>",
            "🔍 搜索会议: \"找找关于 XXX 的会议\"<br>",
            "",
        ])
        return "\n".join(lines)
    lines.append(f"检测到您今天有 {n} 个进行中的会议（按开始时间从新到旧）：")
    if n > 1:
        lines.append("**优先推荐您关注最新的一条（第 1 条）。**")
    lines.append("")
    for i, m in enumerate(in_progress, 1):
        name = m.get("name") or "(无标题)"
        create_time = _format_time_zh(m.get("create_time"))
        prefix = "⭐ " if i == 1 and n > 1 else ""
        lines.append(f"**{prefix}{i}. {name}**<br>")
        lines.append(f"📅 开始时间: {create_time}<br>")
        lines.append("📊 状态: 进行中<br>")
        lines.append("")
    lines.extend([
        "---",
        "💡 **我可以帮您：**",
        "",
        "📝 实时总结: \"帮我总结一下这个会议\"<br>",
        "⏰ 回顾时段: \"最近 30 分钟讲了什么？\"<br>",
        "🔍 搜索内容: \"有没有提到 XXX？\"<br>",
        "✅ 提取待办: \"有哪些需要做的？\"<br>",
        "",
        "现在会议正在录制中，您想了解什么？",
    ])
    return "\n".join(lines)


class Formatter:
    """对外格式化封装，兼容原有命名。"""

    @staticmethod
    def format_meetings(meetings: list[dict], title: str, max_items: int = 10) -> str:
        return format_meeting_list(meetings, title, max_items)

    @staticmethod
    def format_time(iso_time: str | None) -> str:
        return _format_time_zh(iso_time)

    @staticmethod
    def duration(ms: int | None) -> str:
        return _duration_str(ms)

    @staticmethod
    def truncate_summary(summary: str | None, max_len: int = 100) -> str:
        if not summary:
            return ""
        return summary if len(summary) <= max_len else summary[:max_len] + "..."
