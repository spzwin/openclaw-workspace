#!/usr/bin/env python3
"""
todos / complete 脚本
用途：完成待办事项
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

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/todo/completeTodo"

def call_api(app_key, todo_id, content, operate=None):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    payload = {
        "todoId": int(todo_id),
        "content": content
    }
    if operate in ["agree", "disagree"]:
        payload["operate"] = operate

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("todo_id")
    parser.add_argument("--content", required=True)
    parser.add_argument("--operate", choices=["agree", "disagree"])
    args = parser.parse_args()
    result = call_api(app_key, args.todo_id, args.content, args.operate)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
