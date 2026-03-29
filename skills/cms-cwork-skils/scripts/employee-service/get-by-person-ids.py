#!/usr/bin/env python3
"""
employee-service / get-by-person-ids 脚本
用途：根据 corpId 和 personId 列表批量获取员工信息
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


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-user/employee/getByPersonIds"


def _parse_ids(raw: str):
    values = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            values.append(int(item))
    return values


def call_api(app_key: str, corp_id: str, person_ids_raw: str):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    body = json.dumps(_parse_ids(person_ids_raw)).encode("utf-8")
    req = urllib.request.Request(f"{API_URL}/{corp_id}", data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="根据 corpId 和 personId 列表批量获取员工信息")
    parser.add_argument("corp_id", nargs="?", default="", help="corpId，兼容旧的位置参数用法")
    parser.add_argument("person_ids", nargs="?", default="", help="逗号分隔的 personId 列表，兼容旧的位置参数用法")
    parser.add_argument("--corp-id", dest="corp_id_opt", default="", help="企业 corpId")
    parser.add_argument("--person-ids", dest="person_ids_opt", default="", help="逗号分隔的 personId 列表")
    args = parser.parse_args()
    corp_id = args.corp_id_opt or args.corp_id
    person_ids = args.person_ids_opt or args.person_ids
    if not corp_id or not person_ids:
        parser.error("请提供 corpId 和 personId 列表")
    app_key = _resolve_app_key()
    result = call_api(app_key, corp_id, person_ids)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
