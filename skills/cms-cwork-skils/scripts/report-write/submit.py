#!/usr/bin/env python3
"""
report-write / submit 脚本
用途：发送汇报
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


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/record/submit"


def _parse_long_list(raw: str):
    if not raw:
        return []
    values = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            values.append(int(item))
    return values


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


def build_payload(args):
    direct_payload = _load_json_arg(args.body_json, args.body_file)
    if direct_payload is not None:
        return direct_payload

    if not args.main or not args.content_html:
        print("错误: 简单模式下必须提供 --main 和 --content-html", file=sys.stderr)
        sys.exit(1)

    payload = {
        "main": args.main,
        "contentHtml": args.content_html,
        "contentType": args.content_type,
        "typeId": args.type_id,
    }
    if args.plan_id is not None:
        payload["planId"] = args.plan_id
    if args.template_id is not None:
        payload["templateId"] = args.template_id
    if args.grade:
        payload["grade"] = args.grade
    if args.privacy_level:
        payload["privacyLevel"] = args.privacy_level
    if args.accept_emp_ids:
        payload["acceptEmpIdList"] = _parse_long_list(args.accept_emp_ids)
    if args.copy_emp_ids:
        payload["copyEmpIdList"] = _parse_long_list(args.copy_emp_ids)
    if args.report_level_json:
        payload["reportLevelList"] = _parse_json_list(args.report_level_json)
    if args.file_list_json:
        payload["fileVOList"] = _parse_json_list(args.file_list_json)
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
    parser.add_argument("--main")
    parser.add_argument("--content-html")
    parser.add_argument("--content-type", default="html")
    parser.add_argument("--plan-id", type=int)
    parser.add_argument("--template-id", type=int)
    parser.add_argument("--type-id", type=int, default=9999)
    parser.add_argument("--grade", default="")
    parser.add_argument("--privacy-level", default="")
    parser.add_argument("--accept-emp-ids", default="")
    parser.add_argument("--copy-emp-ids", default="")
    parser.add_argument("--report-level-json", default="")
    parser.add_argument("--file-list-json", default="")
    parser.add_argument("--body-json", default="")
    parser.add_argument("--body-file", default="")
    args = parser.parse_args()

    payload = build_payload(args)
    result = call_api(app_key, payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
