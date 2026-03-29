#!/usr/bin/env python3
"""
file-service / upload-file 脚本
用途：上传本地文件并返回资源 ID
"""
import argparse
import json
import mimetypes
import os
import ssl
import sys
import urllib.request
import uuid


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-file/uploadWholeFile"


def _build_multipart_body(file_path: str):
    boundary = f"----CodexBoundary{uuid.uuid4().hex}"
    file_name = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body = b"".join(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode("utf-8"),
            f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return boundary, body


def call_api(app_key: str, file_path: str):
    if not os.path.isfile(file_path):
        print(f"错误: 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    boundary, body = _build_multipart_body(file_path)
    headers = {
        "appKey": app_key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="上传本地文件并返回资源 ID")
    parser.add_argument("file_path", nargs="?", default="", help="本地文件路径，兼容旧的位置参数用法")
    parser.add_argument("--file", dest="file_path_opt", default="", help="本地文件路径")
    args = parser.parse_args()
    file_path = args.file_path_opt or args.file_path
    if not file_path:
        parser.error("请提供文件路径作为参数")
    app_key = _resolve_app_key()
    result = call_api(app_key, file_path)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
