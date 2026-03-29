#!/usr/bin/env python3
"""
report-write / reply 脚本
用途：回复汇报
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


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/record/reply"


def _load_json_arg(body_json: str, body_file: str):
    if body_json:
        return json.loads(body_json)
    if body_file:
        with open(body_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _parse_json_list(raw: str):
    if not raw:
        return []
    return json.loads(raw)


def _parse_str_list(raw: str):
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_bool(raw: str):
    value = raw.strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise ValueError(f"无效布尔值: {raw}")


def build_payload(args):
    direct_payload = _load_json_arg(args.body_json, args.body_file)
    if direct_payload is not None:
        return direct_payload

    if not args.report_record_id or not args.content_html:
        print("错误: 简单模式下必须提供 --report-record-id 和 --content-html", file=sys.stderr)
        sys.exit(1)

    payload = {
        "reportRecordId": args.report_record_id,
        "contentHtml": args.content_html,
    }
    if args.media_list_json:
        media_list = _parse_json_list(args.media_list_json)
        payload["mediaVOList"] = media_list
        payload["isMedia"] = 1
    elif args.is_media is not None:
        payload["isMedia"] = args.is_media
    if args.send_msg:
        payload["sendMsg"] = _parse_bool(args.send_msg)
    if args.add_emp_ids:
        payload["addEmpIdList"] = _parse_str_list(args.add_emp_ids)
    return payload


def call_api(app_key: str, payload: dict):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-record-id", default="")
    parser.add_argument("--content-html", default="")
    parser.add_argument("--is-media", type=int, choices=[0, 1])
    parser.add_argument("--media-list-json", default="")
    parser.add_argument("--send-msg", default="")
    parser.add_argument("--add-emp-ids", default="")
    parser.add_argument("--body-json", default="")
    parser.add_argument("--body-file", default="")
    args = parser.parse_args()

    payload = build_payload(args)
    result = call_api(app_key, payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
