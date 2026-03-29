# 慧记 API 客户端 - 会议列表、分片转写等
import os
import requests
import urllib3
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

# 慧记 API 使用不被系统信任的证书链，关闭 SSL 校验避免请求失败；内部服务网络可控
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 进行中会议「当天」以国内时区为准，避免依赖系统时区
_DEFAULT_TZ = timezone(timedelta(hours=8))

from .config_loader import get_config
from .cache import CacheManager


# 状态映射：combineState 0=录制中, 2=已完成
STATUS_MAP = {
    0: {"status": "recording", "status_text": "进行中"},
    2: {"status": "completed", "status_text": "已完成"},
}

# 进行中会议扫描条数：只看最近 N 条会议（性能/耗时控制）
IN_PROGRESS_SCAN_SIZE = 3
# 列表侧过滤扫描条数：日期范围/最近N天等只在最近 N 条内过滤（不做分页扩展）
LIST_FILTER_SCAN_SIZE = 10


def _ms_to_iso(ms: Optional[int]) -> Optional[str]:
    if ms is None or ms == 0:
        return None
    from datetime import datetime
    return datetime.utcfromtimestamp(ms / 1000.0).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _format_meeting_item(item: dict) -> dict:
    combine_state = item.get("combineState", 2)
    info = STATUS_MAP.get(combine_state, {"status": "completed", "status_text": "已完成"})
    return {
        "name": item.get("name", ""),
        "person_id": item.get("personId"),
        "meeting_id": item.get("_id"),
        "_id": item.get("_id"),
        "combine_state": combine_state,
        "meeting_length": item.get("meetingLength"),
        "status": info["status"],
        "status_text": info["status_text"],
        "create_time": _ms_to_iso(item.get("createTime")),
        "finish_time": _ms_to_iso(item.get("finishTime")),
        "is_in_progress": combine_state == 0,
        "file_url": item.get("fileUrl"),
        "summary": item.get("simpleSummary"),
        "tidy_text": item.get("tidyText"),
        "keyword_list": item.get("keywordList") or [],
        "extra": item.get("extra"),
    }


class MeetingClient:
    """慧记会议 API 客户端。"""

    def __init__(self, app_key: Optional[str] = None):
        cfg = get_config()
        self.api_url = cfg["api_base_url"]
        self.split_record_url = cfg.get("split_record_url") or (
            "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/splitRecordList"
        )
        self.report_info_url = cfg.get("report_info_url") or (
            "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/report/reportInfo"
        )
        self.check_second_stt_url = cfg.get("check_second_stt_url") or (
            "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/checkSecondSttV2"
        )
        self.app_key = app_key or cfg["app_key"] or os.environ.get("XG_BIZ_API_KEY", "")
        self._cache = CacheManager(
            ttl_ms=cfg["cache"].get("ttl", 60000),
            max_size=cfg["cache"].get("maxSize", 100),
        )
        self._session = requests.Session()
        self._session.verify = False

    def get_meetings(
        self,
        page_num: int = 0,
        page_size: int = 10,
        sort_key: str = "createTime",
        name_blur: Optional[str] = None,
        force_refresh: bool = False,
        **kwargs: Any,
    ) -> dict:
        params = {
            "pageNum": page_num,
            "pageSize": page_size,
            "sortKey": sort_key,
            "chatTypeList": kwargs.get("chat_type_list"),
            "nameBlur": name_blur or kwargs.get("name_blur"),
            "limit": "",
        }
        cache_key = str(sorted(params.items()))
        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        resp = self._session.post(
            self.api_url,
            headers={
                "appKey": self.app_key,
                "Content-Type": "application/json; charset=utf-8",
            },
            json=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("resultCode") == 1 and data.get("data", {}).get("pageContent") is not None:
            page_content = data["data"]["pageContent"]
            total = data["data"].get("total", len(page_content))
            meetings = [_format_meeting_item(item) for item in page_content]
        elif data.get("resultCode") == 200 and data.get("data", {}).get("records") is not None:
            # chatListByPage 的另一种返回形态：resultCode=200 时用 data.records（字段 meetingName/meetingId/content），与 resultCode=1 的 data.pageContent 结构不同
            records = data["data"]["records"]
            total = data["data"].get("total", len(records))
            meetings = [
                {
                    "name": r.get("meetingName", ""),
                    "meeting_id": r.get("meetingId"),
                    "_id": r.get("meetingId"),
                    "create_time": _ms_to_iso(r.get("createTime")),
                    "status": "unknown",
                    "status_text": "未知",
                    "is_in_progress": True,
                    "summary": r.get("content"),
                    "tidy_text": None,
                    "keyword_list": [],
                }
                for r in records
            ]
        else:
            raise RuntimeError(f"API 返回错误: {data.get('resultMsg', data)}")

        result = {"total": total, "meetings": meetings}
        self._cache.set(cache_key, result)
        return result

    def get_in_progress_meetings(self, force_refresh: bool = False) -> list[dict]:
        """获取「进行中」会议：仅当天的、且 API 状态为录制中(combineState=0)。
        历史未关闭的不算进行中。当天以 Asia/Shanghai 时区为准。"""
        # 只扫描最近 N 条会议，避免拉取过多数据
        result = self.get_meetings(page_size=IN_PROGRESS_SCAN_SIZE, force_refresh=force_refresh)
        today_local = datetime.now(_DEFAULT_TZ).date()
        out = []
        for m in result["meetings"]:
            if not m.get("is_in_progress"):
                continue
            ct = m.get("create_time")
            if not ct:
                continue
            try:
                dt_utc = datetime.fromisoformat(ct.replace("Z", "+00:00"))
                if dt_utc.tzinfo is None:
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                dt_local = dt_utc.astimezone(_DEFAULT_TZ)
                if dt_local.date() != today_local:
                    continue
            except Exception:
                continue
            out.append(m)
        out.sort(key=lambda x: x.get("create_time") or "", reverse=True)
        return out

    def get_recent_days_meetings(self, days: int, force_refresh: bool = False) -> list[dict]:
        import datetime
        # 仅扫描最近 N 条会议做客户端过滤（不做分页扩展）
        result = self.get_meetings(page_size=LIST_FILTER_SCAN_SIZE, force_refresh=force_refresh)
        threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        out = []
        for m in result["meetings"]:
            ct = m.get("create_time")
            if not ct:
                continue
            try:
                # 解析 ISO 时间
                dt = datetime.datetime.fromisoformat(ct.replace("Z", "+00:00"))
                if dt.replace(tzinfo=None) >= threshold:
                    out.append(m)
            except Exception:
                out.append(m)
        out.sort(key=lambda x: x.get("create_time") or "", reverse=True)
        return out

    def get_split_record_list(self, meeting_chat_id: str) -> dict:
        if not meeting_chat_id:
            raise ValueError("meeting_chat_id 不能为空")
        resp = self._session.post(
            self.split_record_url,
            headers={
                "Content-Type": "application/json",
                "appKey": self.app_key,
            },
            json={"meetingChatId": meeting_chat_id},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_content_in_time_range(
        self,
        meeting_chat_id: str,
        start_time: "datetime.datetime",
        end_time: "datetime.datetime",
    ) -> dict:
        import datetime
        if not meeting_chat_id:
            raise ValueError("meeting_chat_id 不能为空")
        data = self.get_split_record_list(meeting_chat_id)
        records = (data.get("data") or []) if isinstance(data, dict) else []
        if not records:
            return {"data": []}
        filtered = []
        for r in records:
            rt = r.get("realTime")
            if rt is None:
                continue
            if isinstance(rt, (int, float)):
                t = datetime.datetime.utcfromtimestamp(rt / 1000.0 if rt > 1e12 else rt)
            else:
                t = datetime.datetime.fromisoformat(str(rt).replace("Z", "+00:00"))
            if start_time <= t <= end_time:
                filtered.append(r)
        filtered.sort(key=lambda x: x.get("realTime") or 0)
        return {"data": filtered}

    def get_last_n_minutes_content(self, meeting_chat_id: str, minutes: int) -> dict:
        import datetime
        if not meeting_chat_id or minutes <= 0:
            raise ValueError("meeting_chat_id 不能为空且 minutes 必须大于 0")
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(minutes=minutes)
        return self.get_content_in_time_range(meeting_chat_id, start, end)

    def get_report_info(self, meeting_chat_id: str) -> dict:
        """获取会议详情/结构化报告。请求体：meetingChatId。
        服务端可能返回 HTTP 200 且 body 内 resultCode=401（无权限），无 data，调用方需降级。"""
        if not meeting_chat_id:
            raise ValueError("meeting_chat_id 不能为空")
        resp = self._session.post(
            self.report_info_url,
            headers={
                "Content-Type": "application/json",
                "appKey": self.app_key,
            },
            json={"meetingChatId": meeting_chat_id},
            timeout=30,
        )
        if resp.status_code != 200:
            resp.raise_for_status()
        out = resp.json()
        # 业务 401：HTTP 200 但 body 里 resultCode=401，无 data
        if out.get("resultCode") == 401 and "data" not in out:
            out = {"resultCode": 401, "resultMsg": out.get("resultMsg", "no permission"), "data": None}
        return out

    def get_check_second_stt(self, meeting_chat_id: str, show_hidden: bool = False) -> dict:
        """获取修正后的转写（含发言人）。返回 data.stPartList 为列表。"""
        if not meeting_chat_id:
            raise ValueError("meeting_chat_id 不能为空")
        resp = self._session.post(
            self.check_second_stt_url,
            headers={
                "Content-Type": "application/json",
                "appKey": self.app_key,
            },
            json={"meetingChatId": meeting_chat_id, "showHidden": show_hidden},
            timeout=30,
        )
        if resp.status_code == 401:
            return {"resultCode": 401, "resultMsg": "no permission", "data": None}
        resp.raise_for_status()
        return resp.json()

    def is_meeting_in_progress(self, meeting_id: str, force_refresh: bool = False) -> bool | None:
        """根据会议 ID 判断是否「进行中」。True=进行中，False=已结束，None=未找到。"""
        # 仅扫描最近 N 条会议判断状态（不做分页扩展）
        result = self.get_meetings(page_size=LIST_FILTER_SCAN_SIZE, force_refresh=force_refresh)
        for m in result.get("meetings") or []:
            if m.get("_id") == meeting_id or m.get("meeting_id") == meeting_id:
                return bool(m.get("is_in_progress"))
        return None

    def get_meetings_by_date_range(
        self,
        start_date: "datetime.date | str",
        end_date: "datetime.date | str",
        force_refresh: bool = False,
    ) -> list[dict]:
        """按日期范围查询会议（在最近 N 条内过滤；不做分页扩展）。start_date/end_date 为 date 或 'YYYY-MM-DD'。"""
        import datetime as dt
        if isinstance(start_date, str):
            start_date = dt.datetime.strptime(start_date[:10], "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = dt.datetime.strptime(end_date[:10], "%Y-%m-%d").date()
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        result = self.get_meetings(page_size=LIST_FILTER_SCAN_SIZE, force_refresh=force_refresh)
        out = []
        for m in result["meetings"]:
            ct = m.get("create_time")
            if not ct:
                continue
            try:
                # create_time 为 ISO 字符串，转为 Asia/Shanghai 本地日期再比较
                utc_dt = dt.datetime.fromisoformat(ct.replace("Z", "+00:00"))
                if utc_dt.tzinfo is None:
                    utc_dt = utc_dt.replace(tzinfo=timezone.utc)
                d = utc_dt.astimezone(_DEFAULT_TZ).date()
                if start_date <= d <= end_date:
                    out.append(m)
            except Exception:
                continue
        out.sort(key=lambda x: x.get("create_time") or "", reverse=True)
        return out
