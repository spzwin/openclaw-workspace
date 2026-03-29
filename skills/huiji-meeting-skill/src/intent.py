# 意图管理：解析用户查询并返回会议列表/进行中/最近N天/日期范围等
import re
from datetime import date, timedelta
from typing import Any

from .client import MeetingClient
from .formatter import Formatter

# 模糊查询（标题关键词）约束：只取最近 N 条接口结果（不做分页扩展）
SEARCH_PAGE_SIZE = 10  # chatListByPage(nameBlur=...) 最多拉取条数


def _parse_date_range_from_query(query: str) -> tuple[date, date] | None:
    """解析查询中的日期或日期范围，返回 (start_date, end_date)。未匹配返回 None。"""
    today = date.today()
    year = today.year

    # "3月10日到3月15日" / "3月10日-3月15日" / "3月10号至3月15号"
    m = re.search(r"(\d{1,2})月(\d{1,2})[日号]?\s*[到\-至]\s*(\d{1,2})月(\d{1,2})[日号]?", query)
    if m:
        m1, d1, m2, d2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        try:
            start_date = date(year, m1, d1)
            end_date = date(year, m2, d2)
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            return start_date, end_date
        except ValueError:
            return None

    # "3月10日" / "3月10号" 的会议（单日）
    m = re.search(r"(\d{1,2})月(\d{1,2})[日号]", query)
    if m:
        try:
            d = date(year, int(m.group(1)), int(m.group(2)))
            return d, d
        except ValueError:
            return None

    # "3月" 的会议（整月）
    m = re.search(r"(\d{1,2})月\s*(?:的)?(?:会议|记录)?", query)
    if m and not re.search(r"\d{1,2}月\d{1,2}", query):
        try:
            from calendar import monthrange
            month = int(m.group(1))
            _, last = monthrange(year, month)
            return date(year, month, 1), date(year, month, last)
        except (ValueError, IndexError):
            return None

    # "上个月"
    if re.search(r"上个月", query):
        from calendar import monthrange
        if today.month > 1:
            first = date(year, today.month - 1, 1)
        else:
            first = date(year - 1, 12, 1)
        _, last_day = monthrange(first.year, first.month)
        end = date(first.year, first.month, last_day)
        return first, end

    # "上周"（过去 7 天）
    if re.search(r"上周", query):
        end = today
        start = today - timedelta(days=6)
        return start, end

    return None


class IntentManager:
    DEFAULT_COUNT = 3
    MAX_LIST_COUNT = 20

    def __init__(self, client: MeetingClient | None = None):
        self.client = client or MeetingClient()
        self.formatter = Formatter()

    def understand(self, query: str) -> dict:
        """理解用户意图并执行，返回 { title, total, meetings, timestamp }。"""
        query = (query or "").strip()

        # 日期范围 / 单日 / 整月 / 上周 / 上个月
        dr = _parse_date_range_from_query(query)
        if dr is not None:
            start_date, end_date = dr
            meetings = self.client.get_meetings_by_date_range(start_date, end_date, force_refresh=True)
            if start_date == end_date:
                title = f"{start_date.year}年{start_date.month}月{start_date.day}日的会议记录"
            else:
                title = f"{start_date.month}月{start_date.day}日 至 {end_date.month}月{end_date.day}日的会议记录"
            return self._result(meetings, title)

        # 最近 N 天
        m = re.search(r"(?:最新|最近|最新的|最近的)\s*(\d+)?\s*(天|日)\s*(?:会议|记录)", query, re.I)
        if m:
            days = int(m.group(1)) if m.group(1) else 7
            meetings = self.client.get_recent_days_meetings(days, force_refresh=True)
            return self._result(meetings, f"最近{days}天的会议记录")

        # 最近 N 条
        m = re.search(r"(?:最新|最近|最新的|最近的)\s*(\d+)?\s*(条|个|记录|会议)", query, re.I)
        if m:
            requested = int(m.group(1)) if m.group(1) else self.DEFAULT_COUNT
            if requested > self.MAX_LIST_COUNT:
                count = self.MAX_LIST_COUNT
                title = f"最近{count}条会议记录（已按上限{self.MAX_LIST_COUNT}条返回）"
            else:
                count = requested
                title = f"最近{count}条会议记录"
            result = self.client.get_meetings(page_num=0, page_size=count, force_refresh=True)
            return self._result(result["meetings"], title)

        # 进行中
        if re.search(r"(?:正在进行中|进行中|当前|现在)\s*(?:会议|记录)", query, re.I):
            meetings = self.client.get_in_progress_meetings(force_refresh=True)
            return self._result(meetings, "正在进行中的会议")

        # 已完成
        if re.search(r"(?:完成|已完成|结束)\s*(?:会议|记录)", query, re.I):
            result = self.client.get_meetings(page_num=0, page_size=10)
            meetings = [m for m in result["meetings"] if m.get("status") == "completed"]
            return self._result(meetings, "已完成的会议")

        # 处理中
        if re.search(r"(?:处理中|未完成)\s*(?:会议|记录)", query, re.I):
            result = self.client.get_meetings(page_num=0, page_size=10)
            meetings = [m for m in result["meetings"] if m.get("status") == "processing"]
            return self._result(meetings, "处理中的会议")

        # 默认：帮我看下 / 查看 / 查询 等 → 最近 N 条
        if re.search(r"帮我看下|查看|查询|看看|显示|展示", query, re.I):
            result = self.client.get_meetings(page_num=0, page_size=self.DEFAULT_COUNT, force_refresh=True)
            return self._result(result["meetings"], f"最近{self.DEFAULT_COUNT}条会议记录")

        # 默认
        result = self.client.get_meetings(page_num=0, page_size=self.DEFAULT_COUNT, force_refresh=True)
        return self._result(result["meetings"], "最新的会议记录")

    def _result(self, meetings: list[dict], title: str) -> dict:
        return {
            "title": title,
            "total": len(meetings),
            "meetings": meetings,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }


def search_meetings(
    client: MeetingClient,
    keyword: str,
    page_size: int = SEARCH_PAGE_SIZE,
) -> list[dict]:
    """按关键词模糊搜索会议：仅走接口 nameBlur（名称模糊搜索），不做本地二次打分，最多返回 page_size 条。"""
    raw = (keyword or "").strip()
    if not raw:
        return []
    result = client.get_meetings(page_num=0, page_size=page_size, name_blur=raw, force_refresh=True)
    return result["meetings"]
