#!/usr/bin/env python3
"""
employee-service / get-org-info 脚本
用途：获取员工组织架构信息
"""
import argparse
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-user/employee/getEmployeeOrgInfo"


def call_api(app_key: str, emp_id: str):
    headers = {"appKey": app_key}
    query = f"?empId={urllib.parse.quote(emp_id)}"
    req = urllib.request.Request(API_URL + query, headers=headers, method="GET")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="获取员工组织架构信息")
    parser.add_argument("emp_id", nargs="?", default="", help="empId，兼容旧的位置参数用法")
    parser.add_argument("--emp-id", dest="emp_id_opt", default="", help="员工 empId")
    args = parser.parse_args()
    emp_id = args.emp_id_opt or args.emp_id
    if not emp_id:
        parser.error("请提供 empId 作为参数")
    app_key = _resolve_app_key()
    result = call_api(app_key, emp_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
