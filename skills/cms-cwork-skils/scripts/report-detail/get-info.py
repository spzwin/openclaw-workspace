#!/usr/bin/env python3
"""
report-detail / get-info 脚本
用途：获取单篇汇报的结构化详情
"""
import argparse
import sys, os, json, urllib.request, urllib.parse, ssl


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/info"

def call_api(app_key, report_id):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    query = f"?reportId={urllib.parse.quote(report_id)}"
    req = urllib.request.Request(API_URL + query, headers=headers, method="GET")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    parser = argparse.ArgumentParser(description="获取单篇汇报的结构化详情")
    parser.add_argument("report_id", nargs="?", default="", help="reportId，兼容旧的位置参数用法")
    parser.add_argument("--report-id", dest="report_id_opt", default="", help="目标汇报 ID")
    args = parser.parse_args()
    report_id = args.report_id_opt or args.report_id
    if not report_id:
        parser.error("请提供 reportId 作为参数")
    app_key = _resolve_app_key()
    result = call_api(app_key, report_id)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
