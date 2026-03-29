#!/usr/bin/env python3
"""
user-search / search-emp 脚本

用途：根据姓名模糊搜索企业内部员工

使用方式：
 python3 scripts/user-search/search-emp.py "张三"

环境变量：
 XG_BIZ_API_KEY / XG_APP_KEY — appKey
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL

def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-user/searchEmpByName"


def call_api(app_key: str, name: str) -> dict:
    """调用搜索接口，返回原始 JSON 响应"""
    headers = {
        "appKey": app_key,
        "Content-Type": "application/json",
    }

    # Query 参数拼接到 URL
    url = f"{API_URL}?searchKey={urllib.parse.quote(name)}"

    req = urllib.request.Request(url, headers=headers, method="GET")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="根据姓名模糊搜索企业内部员工")
    parser.add_argument("keyword", nargs="?", default="", help="搜索关键词，兼容旧的位置参数用法")
    parser.add_argument("--keyword", dest="keyword_opt", default="", help="员工姓名关键词")
    args = parser.parse_args()

    name = args.keyword_opt or args.keyword
    if not name:
        parser.error("请提供搜索姓名作为参数")

    app_key = _resolve_app_key()

    # 1. 调用接口，获取原始 JSON
    result = call_api(app_key, name)

    # 2. 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
