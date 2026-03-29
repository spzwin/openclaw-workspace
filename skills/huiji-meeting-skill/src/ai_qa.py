# 实时会议问答：时间范围解析、内容筛选、提示词生成
import re
from datetime import datetime, timedelta
from typing import Any

from .client import MeetingClient
from .prompts import AI_QA_SYSTEM_PROMPT


def _parse_time_range(question: str) -> dict | None:
    """解析用户时间范围提问。"""
    # "会议开始20分钟的内容" / "从开始到20分钟" / "开始后30分钟"
    m = re.search(r"(?:会议开始|从开始到|开始的|开始后)(\d+)(?:分钟的内容|分钟内容|分钟)?", question, re.I)
    if m:
        return {"type": "start_to_minutes", "minutes": int(m.group(1)), "description": f"会议开始到{m.group(1)}分钟的内容"}

    # "最后10分钟"（会议最后 N 分钟，以会议结束为基准）
    m = re.search(r"最后(\d+)(?:分钟的内容|分钟内容|分钟)", question, re.I)
    if m:
        return {"type": "last_n_minutes_of_meeting", "minutes": int(m.group(1)), "description": f"会议最后{m.group(1)}分钟的内容"}

    # "最近20分钟" / "刚才30分钟"（以当前时间为基准）
    m = re.search(r"(最近|刚才|刚刚)(\d+)(分钟|半小时|小时)", question, re.I)
    if m:
        unit = m.group(3)
        n = int(m.group(2))
        if "半" in unit:
            n = 30
        elif "小时" in unit:
            n = n * 60
        return {"type": "last_n_minutes", "minutes": n, "description": f"{m.group(1)}{n}分钟的内容"}

    # "结束前10分钟" / "开始到前10分钟"
    m = re.search(r"(?:结束前|开始到前)(\d+)(?:分钟的内容|分钟内容|分钟)", question, re.I)
    if m:
        return {"type": "start_to_end_minus_minutes", "minutes": int(m.group(1)), "description": f"会议开始到结束前{m.group(1)}分钟的内容"}

    # "第15-25分钟" / "15到25分钟"
    m = re.search(r"第?(\d+)[-到](\d+)(?:分钟的内容|分钟内容)?", question, re.I)
    if m:
        return {
            "type": "minutes_range",
            "start_minutes": int(m.group(1)),
            "end_minutes": int(m.group(2)),
            "description": f"第{m.group(1)}-{m.group(2)}分钟的内容",
        }

    # "整个会议" / "全部内容"
    if re.search(r"整个会议|全部内容|所有内容|主要内容", question, re.I):
        return {"type": "full_meeting", "description": "整个会议的内容"}

    return None


def _to_ms(rt: Any) -> int | None:
    if rt is None:
        return None
    if isinstance(rt, (int, float)):
        return int(rt) if rt > 1e12 else int(rt * 1000)
    try:
        return int(datetime.fromisoformat(str(rt).replace("Z", "+00:00")).timestamp() * 1000)
    except Exception:
        return None


def _filter_by_time_range(records: list[dict], time_range: dict) -> str:
    """按时间范围筛选分片记录的文本并拼接。"""
    meeting_start_ms = None
    meeting_end_ms = None
    for r in records:
        ms = _to_ms(r.get("realTime") or r.get("startTime"))
        if ms is not None:
            meeting_start_ms = min(meeting_start_ms, ms) if meeting_start_ms is not None else ms
            meeting_end_ms = max(meeting_end_ms, ms) if meeting_end_ms is not None else ms
    if meeting_start_ms is None:
        meeting_start_ms = 0
    if meeting_end_ms is None:
        meeting_end_ms = meeting_start_ms

    texts = []
    t = time_range.get("type")
    now_ms = int(datetime.utcnow().timestamp() * 1000)

    for r in records:
        if not r.get("text"):
            continue
        ts_ms = _to_ms(r.get("realTime") or r.get("startTime"))
        if ts_ms is None:
            if t == "full_meeting":
                texts.append(r["text"])
            continue
        if t == "start_to_minutes":
            end_ms = meeting_start_ms + time_range["minutes"] * 60 * 1000
            if ts_ms <= end_ms:
                texts.append(r["text"])
        elif t == "last_n_minutes":
            start_ms = now_ms - time_range["minutes"] * 60 * 1000
            if start_ms <= ts_ms <= now_ms:
                texts.append(r["text"])
        elif t == "last_n_minutes_of_meeting":
            start_ms = meeting_end_ms - time_range["minutes"] * 60 * 1000
            if start_ms <= ts_ms <= meeting_end_ms:
                texts.append(r["text"])
        elif t == "start_to_end_minus_minutes":
            end_ms = meeting_end_ms - time_range["minutes"] * 60 * 1000
            if meeting_start_ms <= ts_ms <= end_ms:
                texts.append(r["text"])
        elif t == "minutes_range":
            start_ms = meeting_start_ms + time_range["start_minutes"] * 60 * 1000
            end_ms = meeting_start_ms + time_range["end_minutes"] * 60 * 1000
            if start_ms <= ts_ms <= end_ms:
                texts.append(r["text"])
        else:
            texts.append(r["text"])
    return "\n".join(texts)


class AIQA:
    """会议实时问答：时间范围解析、获取内容、生成 AI 提示词。"""

    def __init__(self, client: MeetingClient | None = None):
        self.client = client or MeetingClient()

    def parse_time_range_question(self, question: str) -> dict | None:
        return _parse_time_range(question)

    async def get_full_meeting_content(self, meeting_id: str) -> dict:
        """获取指定会议的完整转写内容。"""
        data = self.client.get_split_record_list(meeting_id)
        records = (data.get("data") or []) if isinstance(data, dict) else []
        if not records:
            return {"content": "", "records": []}
        sorted_records = sorted(records, key=lambda x: x.get("realTime") or x.get("startTime") or 0)
        content = "\n".join(r.get("text", "") or "" for r in sorted_records if r.get("text"))
        return {"content": content, "records": sorted_records}

    def _format_speaker_records(self, st_part_list: list[dict]) -> tuple[str, list[dict]]:
        """将 checkSecondSttV2 的 stPartList 转为正文与 records（供时间范围筛选）。"""
        lines = []
        records = []
        for part in st_part_list:
            speaker = (part.get("speakerName") or "").strip() or "未知"
            text = (part.get("rewriteText") or "").strip()
            if not text:
                continue
            start_ms = part.get("startTime")
            if start_ms is not None and isinstance(start_ms, (int, float)):
                ms = int(start_ms) if start_ms > 1e12 else int(start_ms * 1000)
                m, s = divmod(ms // 1000, 60)
                lines.append(f"【{m:02d}:{s:02d}】{speaker}：{text}")
            else:
                lines.append(f"{speaker}：{text}")
            records.append({
                "text": text,
                "startTime": start_ms,
                "realTime": start_ms,
                "speakerName": speaker,
            })
        return "\n".join(lines), records

    def _content_from_split_record_list(self, meeting_id: str) -> dict:
        """仅用 splitRecordList 拉取原文（进行中会议唯一有数据的接口；刚结束时的兜底）。"""
        data = self.client.get_split_record_list(meeting_id)
        records = (data.get("data") or []) if isinstance(data, dict) else []
        if not records:
            return {"content": "", "records": []}
        sorted_records = sorted(records, key=lambda x: x.get("realTime") or x.get("startTime") or 0)
        content = "\n".join(r.get("text", "") or "" for r in sorted_records if r.get("text"))
        return {"content": content, "records": sorted_records, "source": "splitRecordList"}

    def get_full_meeting_content_sync(
        self, meeting_id: str, is_in_progress: bool | None = None
    ) -> dict:
        """按会议状态取内容，符合实际接口数据能力：
        - 进行中：只有 splitRecordList 有实时原文，仅用该接口。
        - 已结束：优先 reportInfo / checkSecondSttV2；若存在时间差（刚结束尚未产出）则用 splitRecordList 兜底。
        is_in_progress 为 None 时自动查一次会议状态。"""
        if is_in_progress is None:
            is_in_progress = self.client.is_meeting_in_progress(meeting_id)
            # 未查到视为已结束，走已结束逻辑
            if is_in_progress is None:
                is_in_progress = False

        if is_in_progress:
            return self._content_from_split_record_list(meeting_id)

        # 已结束：reportInfo → checkSecondSttV2 → splitRecordList（时间差兜底）
        try:
            report = self.client.get_report_info(meeting_id)
            if report.get("resultCode") == 1 and report.get("data"):
                text_report = report["data"].get("textReport") or report["data"].get("text_report")
                if text_report and len(text_report.strip()) >= 50:
                    return {"content": text_report.strip(), "records": [], "source": "reportInfo"}
        except Exception:
            pass

        try:
            stt = self.client.get_check_second_stt(meeting_id)
            if stt.get("resultCode") == 1 and stt.get("data"):
                st_part_list = stt["data"].get("stPartList") or []
                if st_part_list:
                    content, records = self._format_speaker_records(st_part_list)
                    if len(content) >= 50:
                        return {"content": content, "records": records, "source": "checkSecondSttV2"}
        except Exception:
            pass

        return self._content_from_split_record_list(meeting_id)

    def filter_content_by_time_range(self, records: list[dict], time_range: dict) -> str:
        """根据时间范围筛选记录文本。"""
        return _filter_by_time_range(records, time_range)

    def generate_ai_prompt(self, question: str, meeting_content: str, time_range: dict | None = None) -> str:
        """生成给大模型的提示词。"""
        prompt = AI_QA_SYSTEM_PROMPT + "\n\n"
        if time_range:
            prompt += f"## 用户问题\n用户需要获取：{time_range.get('description', '')}\n\n"
            prompt += (
                "## 输出要求（强制）\n"
                "1. 必须对该时间段内容做**综合总结**（按主题/要点归纳），禁止按分钟或时间轴逐条展示（禁止【会议进行到 XX:XX】一段一段罗列）。\n"
                "2. 除非用户明确要求“原文/逐句/谁说了什么”，否则不得使用时间轴或逐条复述格式。\n"
                "3. 可引用少量原句佐证，总引用不超过 3 条，每条不超过 50 字。\n\n"
            )
        else:
            prompt += f"## 用户问题\n{question}\n\n"
        prompt += f"## 会议内容\n{meeting_content}\n\n"
        prompt += "## 请根据上述要求和会议内容生成回答"
        return prompt

    def handle_question(
        self, meeting_id: str, question: str, is_in_progress: bool | None = None
    ) -> str:
        """处理用户问答：解析时间范围、取内容、生成提示词。进行中会议传 is_in_progress=True。"""
        time_range = self.parse_time_range_question(question)
        full = self.get_full_meeting_content_sync(meeting_id, is_in_progress=is_in_progress)
        if len(full["content"]) < 100:
            return "提供的会议内容不足，无法生成有效的会议报告。请提供完整的会议记录内容。"
        content = full["content"]
        if time_range:
            content = self.filter_content_by_time_range(full["records"], time_range)
            if len(content) < 100:
                return f"在指定的时间范围（{time_range.get('description', '')}）内没有找到足够的会议内容。"
        prompt = self.generate_ai_prompt(question, content, time_range)
        return f"[提示词已生成，可调用 AI 生成回答]\n内容长度: {len(content)} 字\n查询范围: {time_range['description'] if time_range else '全部内容'}\n\n---\n{prompt[:1500]}{'...' if len(prompt) > 1500 else ''}"
