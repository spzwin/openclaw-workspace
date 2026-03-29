#!/usr/bin/env python3
"""测试 reportInfo 接口：打印请求与原始响应，便于核对 URL/方法/参数/返回结构。"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from src.config_loader import get_config
from src.client import MeetingClient

def main():
    cfg = get_config()
    url = cfg.get("report_info_url") or "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/report/reportInfo"
    app_key = os.environ.get("XG_BIZ_API_KEY") or cfg.get("app_key") or ""
    if not app_key:
        print("请设置 XG_BIZ_API_KEY")
        return

    # 取一条已完成的会议 id
    client = MeetingClient()
    result = client.get_meetings(page_num=0, page_size=5, force_refresh=True)
    meetings = [m for m in result["meetings"] if m.get("status") == "completed"]
    if not meetings:
        print("没有已完成的会议，无法测试")
        return
    meeting_id = meetings[0].get("_id") or meetings[0].get("meeting_id")
    print(f"测试 meeting_chat_id: {meeting_id}")
    print(f"请求 URL: {url}")
    print()

    # 当前实现：POST + json body
    print("--- 方式 1: POST application/json body meetingChatId ---")
    resp = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "appKey": app_key,
        },
        json={"meetingChatId": meeting_id},
        timeout=30,
    )
    print(f"status_code: {resp.status_code}")
    print(f"response body (raw): {resp.text[:2000]}")
    try:
        j = resp.json()
        print(f"response keys: {list(j.keys()) if isinstance(j, dict) else 'not dict'}")
        if isinstance(j, dict) and "data" in j:
            print(f"data keys: {list(j['data'].keys()) if isinstance(j.get('data'), dict) else type(j.get('data'))}")
    except Exception as e:
        print(f"json parse: {e}")
    print()

    # 尝试 GET + query
    print("--- 方式 2: GET query meetingChatId ---")
    resp2 = requests.get(
        url,
        headers={"appKey": app_key},
        params={"meetingChatId": meeting_id},
        timeout=30,
    )
    print(f"status_code: {resp2.status_code}, body: {resp2.text[:500]}")
    print()

    # 尝试 POST body 用 meetingId（有的接口用 meetingId）
    print("--- 方式 3: POST body meetingId ---")
    resp3 = requests.post(
        url,
        headers={"Content-Type": "application/json", "appKey": app_key},
        json={"meetingId": meeting_id},
        timeout=30,
    )
    print(f"status_code: {resp3.status_code}, body: {resp3.text[:500]}")
    print()

    # 结论
    j = resp.json()
    if j.get("resultCode") == 401:
        print("结论: 接口返回 HTTP 200，但 body 里 resultCode=401（业务无权限），不是 HTTP 状态码 401。")
        print("      若你本地测试是成功的，请确认：1) 同一 appKey 2) 同一 meeting_id 3) 接口路径是否一致。")
    elif j.get("resultCode") == 1 and j.get("data"):
        print("结论: 调用成功，data 结构见上。")
        if isinstance(j.get("data"), dict):
            print("data 字段:", list(j["data"].keys()))

if __name__ == "__main__":
    main()
