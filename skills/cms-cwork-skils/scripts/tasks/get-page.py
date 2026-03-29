#!/usr/bin/env python3
"""
tasks / get-page 脚本
用途：查询工作任务列表
"""
import argparse, sys, os, json, urllib.request, urllib.parse, ssl


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/plan/searchPage"

def call_api(app_key, page_index=1, page_size=10, search_key="", status="", body_json=""):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    if body_json:
        payload = json.loads(body_json)
    else:
        payload = {
            "pageIndex": page_index,
            "pageSize": page_size
        }
        if search_key:
            payload["keyWord"] = search_key

        status_map = {"DONE": 0, "CANCELLED": 0, "RUNNING": 1, "INIT": 1, "PENDING": 1, "COMPLETED": 0, "0": 0, "1": 1}
        mapped_status = status_map.get(str(status).upper())
        if mapped_status is not None:
            payload["status"] = mapped_status
        
    req_body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=req_body, headers=headers, method="POST")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-index", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--keyword", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--body-json", default="")
    args = parser.parse_args()
    result = call_api(
        app_key,
        page_index=args.page_index,
        page_size=args.page_size,
        search_key=args.keyword,
        status=args.status,
        body_json=args.body_json,
    )
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
