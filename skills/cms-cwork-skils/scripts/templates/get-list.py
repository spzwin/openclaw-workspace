#!/usr/bin/env python3
"""
templates / get-list 脚本
用途：获取最近处理过的事项列表
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

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/template/listTemplates"

def call_api(app_key, limit=50, begin_time=None, end_time=None, body_json=""):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    if body_json:
        payload = json.loads(body_json)
    else:
        payload = {"limit": limit}
        if begin_time is not None:
            payload["beginTime"] = begin_time
        if end_time is not None:
            payload["endTime"] = end_time
    req_body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=req_body, headers=headers, method="POST")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_result(result):
    if result.get("resultCode") == 1 and result.get("data") is None:
        result["data"] = {"recentOperateTemplates": []}
        result["normalizedEmptyData"] = True
    return result

def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--begin-time", type=int)
    parser.add_argument("--end-time", type=int)
    parser.add_argument("--body-json", default="")
    args = parser.parse_args()
    result = call_api(
        app_key,
        limit=args.limit,
        begin_time=args.begin_time,
        end_time=args.end_time,
        body_json=args.body_json,
    )
    result = normalize_result(result)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
