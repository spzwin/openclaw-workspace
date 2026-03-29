#!/usr/bin/env python3
"""
templates / get-by-ids 脚本
用途：按事项 ID 列表批量获取事项简易信息
"""
import argparse
import json
import os
import ssl
import sys
import urllib.request


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/template/listByIds"


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key


def _load_body(body_json: str, body_file: str):
    if body_json:
        return json.loads(body_json)
    if body_file:
        with open(body_file, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return None


def _parse_id_list(raw: str):
    values = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            values.append(int(item))
    return values


def build_payload(args):
    direct_payload = _load_body(args.body_json, args.body_file)
    if direct_payload is not None:
        return direct_payload
    if not args.template_ids:
        print("错误: 简单模式下必须提供 --template-ids", file=sys.stderr)
        sys.exit(1)
    return _parse_id_list(args.template_ids)


def call_api(app_key: str, payload):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(request, context=ctx, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-ids", default="")
    parser.add_argument("--body-json", default="")
    parser.add_argument("--body-file", default="")
    args = parser.parse_args()
    result = call_api(app_key, build_payload(args))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
