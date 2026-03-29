#!/usr/bin/env python3
"""
ai-qa / ask-sse 脚本
用途：对指定汇报集合发起 AI SSE 问答，并合并为最终 JSON
"""
import argparse
import json
import os
import ssl
import sys
import urllib.request


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/report/aiSseQaV2"


def _parse_sse_event(data_content):
    try:
        return json.loads(data_content)
    except json.JSONDecodeError:
        return data_content

def call_api_sse(app_key, content, report_ids_str):
    headers = {"appKey": app_key, "Accept": "text/event-stream", "Content-Type": "application/json"}
    
    report_id_list = []
    for rid in report_ids_str.split(','):
        if rid.strip().isdigit():
            report_id_list.append(int(rid.strip()))
    if not report_id_list:
        print("错误: 请至少提供一个 reportId", file=sys.stderr)
        sys.exit(1)
                
    payload = {
        "userContent": content,
        "aiType": 42,
        "reportIdList": report_id_list
    }
    
    req_body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=req_body, headers=headers, method="POST")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

    answer_parts = []
    metrics = {}
    raw_events = []
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        for line in resp:
            line_str = line.decode("utf-8").strip()
            if line_str.startswith("data:"):
                data_content = line_str[5:].strip()
                if data_content == "[DONE]":
                    break
                event = _parse_sse_event(data_content)
                raw_events.append(event)
                if isinstance(event, dict):
                    content_part = event.get("content")
                    if content_part:
                        answer_parts.append(content_part)
                    event_id = event.get("id")
                    if event_id in {"firstTextDelay", "costMoney", "totalTimeCost"}:
                        metrics[event_id] = {k: v for k, v in event.items() if k != "id"}
                elif isinstance(event, str):
                    if event != "ok":
                        answer_parts.append(event)

    result = {
        "resultCode": 1,
        "data": {
            "answer": "".join(answer_parts).strip(),
        },
    }
    if metrics:
        result["data"]["metrics"] = metrics
    if raw_events:
        result["data"]["eventCount"] = len(raw_events)
    return result

def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("content")
    parser.add_argument("report_ids")
    args = parser.parse_args()
    
    # 获取并输出合并后的 JSON
    result = call_api_sse(app_key, args.content, args.report_ids)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
