#!/usr/bin/env python3
"""
tasks / get-simple-plan-and-report-info 脚本
用途：获取任务简易信息及其关联汇报列表
"""
import argparse
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/plan/getSimplePlanAndReportInfo"


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key


def call_api(app_key: str, plan_id: int):
    query = urllib.parse.urlencode({"planId": plan_id})
    url = f"{API_URL}?{query}"
    request = urllib.request.Request(url, headers={"appKey": app_key}, method="GET")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(request, context=ctx, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-id", type=int, required=True)
    args = parser.parse_args()
    result = call_api(app_key, args.plan_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
