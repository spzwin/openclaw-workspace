#!/usr/bin/env python3
"""
report-query / is-report-read 脚本
用途：判断指定员工是否已读某条汇报
"""
import argparse
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/reportInfoOpenQuery/isReportRead"


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key


def call_api(app_key: str, report_id: int, employee_id: int):
    query = urllib.parse.urlencode({"reportId": report_id, "employeeId": employee_id})
    request = urllib.request.Request(f"{API_URL}?{query}", headers={"appKey": app_key}, method="GET")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(request, context=ctx, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-id", type=int, required=True)
    parser.add_argument("--employee-id", type=int, required=True)
    args = parser.parse_args()
    result = call_api(app_key, args.report_id, args.employee_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
