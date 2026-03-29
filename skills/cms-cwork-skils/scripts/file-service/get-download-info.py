#!/usr/bin/env python3
"""
file-service / get-download-info 脚本
用途：获取文件下载链接与元信息
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


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-file/getDownloadInfo"


def call_api(app_key: str, resource_id: str):
    headers = {"appKey": app_key}
    query = f"?resourceId={urllib.parse.quote(resource_id)}"
    req = urllib.request.Request(API_URL + query, headers=headers, method="GET")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="获取文件下载链接与元信息")
    parser.add_argument("resource_id", nargs="?", default="", help="resourceId，兼容旧的位置参数用法")
    parser.add_argument("--resource-id", dest="resource_id_opt", default="", help="文件资源 ID")
    args = parser.parse_args()
    resource_id = args.resource_id_opt or args.resource_id
    if not resource_id:
        parser.error("请提供 resourceId 作为参数")
    app_key = _resolve_app_key()
    result = call_api(app_key, resource_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
