#!/usr/bin/env python3
"""
report-query / get-todo-list 脚本
用途：获取汇报待办分页列表
"""
import argparse
import json
import os
import ssl
import sys
import urllib.request


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/reportInfoOpenQuery/todoList"
DEFAULT_CLIENT_LIMIT = 200
MAX_CLIENT_LIMIT = 500


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


def build_payload(args):
    direct_payload = _load_body(args.body_json, args.body_file)
    if direct_payload is not None:
        return direct_payload
    return {"pageIndex": args.page_index, "pageSize": args.page_size}


def call_api(app_key: str, payload: dict):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(request, context=ctx, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _resolve_client_limit(client_limit):
    if client_limit is None:
        return DEFAULT_CLIENT_LIMIT
    return min(client_limit, MAX_CLIENT_LIMIT)


def _apply_client_limit(result, client_limit):
    effective_limit = _resolve_client_limit(client_limit)
    data = result.get("data")
    if not isinstance(data, dict):
        return result
    items = data.get("list")
    if not isinstance(items, list):
        return result
    data["serverReturnedSize"] = len(items)
    data["list"] = items[:effective_limit]
    data["clientLimit"] = effective_limit
    data["clientReturnedSize"] = len(data["list"])
    data["defaultClientLimit"] = DEFAULT_CLIENT_LIMIT
    data["maxClientLimit"] = MAX_CLIENT_LIMIT
    if client_limit is not None:
        data["requestedClientLimit"] = client_limit
    return result


def _emit_result(result, output_file):
    text = json.dumps(result, ensure_ascii=False)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as handle:
            handle.write(text)
    print(text)


def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-index", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--body-json", default="")
    parser.add_argument("--body-file", default="")
    parser.add_argument("--client-limit", type=int)
    parser.add_argument("--output-file", default="")
    args = parser.parse_args()
    result = call_api(app_key, build_payload(args))
    result = _apply_client_limit(result, args.client_limit)
    _emit_result(result, args.output_file)


if __name__ == "__main__":
    main()
