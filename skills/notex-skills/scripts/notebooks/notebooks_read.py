#!/usr/bin/env python3
"""
NoteX Notebook 来源读取脚本（可独立执行）

功能：
1) 获取某个 Notebook 下的来源列表（不含正文）
2) 获取某个来源的正文内容（contentText）

⚠️ 独立执行说明：
  本脚本可脱离 AI Agent 直接在命令行运行。
  执行前请先阅读 Notebooks 模块的 OpenAPI 接口文档获取完整入参说明：
  openapi/notebooks/api-index.md

使用方式：
  python3 notex-skills/scripts/notebooks/notebooks_read.py --mode list --notebook-id nb_xxx
  python3 notex-skills/scripts/notebooks/notebooks_read.py --mode content --notebook-id nb_xxx --source-id src_xxx

环境变量：
  XG_USER_TOKEN  — access-token（优先使用）
"""

import argparse
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

PROD_NOTEX_HOST = "notex.aishuo.co"
PROD_NOTEX_BASE_URL = "https://notex.aishuo.co/noteX"


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def _request_json(url: str, *, method: str = "GET", headers: dict = None,
                  timeout: int = 60) -> dict:
    req_headers = dict(headers or {})
    req = urllib.request.Request(url, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"请求失败: {e.reason}") from e

    if isinstance(payload, dict) and "resultCode" in payload:
        if payload["resultCode"] != 1:
            raise RuntimeError(payload.get("resultMsg") or f"API error ({payload['resultCode']})")
        return payload.get("data", {})

    return payload


def _normalize_prod_base_url(raw_url: str) -> str:
    parsed = urllib.parse.urlsplit(raw_url)
    if parsed.scheme != "https":
        raise RuntimeError("base-url 必须使用 https 协议")
    if parsed.hostname != PROD_NOTEX_HOST:
        raise RuntimeError(f"base-url 必须使用生产域名 {PROD_NOTEX_HOST}")
    pathname = parsed.path.rstrip("/")
    if not pathname or pathname == "/":
        return f"{parsed.scheme}://{parsed.hostname}/noteX"
    if pathname in ("/noteX", "/noteX/openapi"):
        return f"{parsed.scheme}://{parsed.hostname}{pathname}"
    raise RuntimeError("base-url 路径仅支持 /noteX 或 /noteX/openapi")


def _build_api_url(base_url: str, api_path: str) -> str:
    normalized = api_path if api_path.startswith("/openapi/") else f"/openapi{api_path.replace('/api', '', 1)}"
    if base_url.endswith("/openapi"):
        return f"{base_url}{normalized.replace('/openapi', '', 1)}"
    if base_url.endswith("/noteX"):
        return f"{base_url}{normalized}"
    raise RuntimeError(f"不支持的 base-url: {base_url}")


# ──────────── 鉴权：统一由 cms-auth-skills 提供 ────────────

def _find_login_py() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dir = script_dir
    for _ in range(10):
        parent = os.path.dirname(search_dir)
        for sub in ["", "skills"]:
            candidate = os.path.join(parent, sub, "cms-auth-skills", "scripts", "auth", "login.py") if sub else \
                        os.path.join(parent, "cms-auth-skills", "scripts", "auth", "login.py")
            if os.path.isfile(candidate):
                return candidate
        search_dir = parent
    return ""


def resolve_access_token(context_json: str = "") -> str:
    env_token = os.environ.get("XG_USER_TOKEN", "").strip()
    if env_token:
        _log("[auth] 使用环境变量鉴权 (XG_USER_TOKEN)")
        return env_token

    login_py = _find_login_py()
    if not login_py:
        raise RuntimeError(
            "未找到 cms-auth-skills/scripts/auth/login.py，请先安装：\n"
            "  npx clawhub@latest install cms-auth-skills --force"
        )

    _log("[auth] 调用 cms-auth-skills login.py 获取 access-token ...")
    cmd = [sys.executable, login_py, "--ensure"]
    if context_json:
        cmd += ["--context-json", context_json]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"鉴权失败: {result.stderr.strip()}")

    token = result.stdout.strip()
    if not token:
        raise RuntimeError("鉴权失败: login.py 未返回 access-token")

    _log("[auth] 鉴权成功")
    return token


# ──────────── 业务功能 ────────────

def list_sources(base_url: str, access_token: str, notebook_id: str,
                 business_type: str = ""):
    if not notebook_id:
        raise RuntimeError("list 模式必须提供 --notebook-id")

    headers = {"Content-Type": "application/json", "access-token": access_token}

    query = ""
    if business_type:
        query = f"?businessType={urllib.parse.quote(business_type)}"

    url = _build_api_url(base_url, f"/api/notebooks/{notebook_id}/sources{query}")
    data = _request_json(url, headers=headers, timeout=60)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def fetch_source_content(base_url: str, access_token: str, notebook_id: str,
                         source_id: str):
    if not notebook_id or not source_id:
        raise RuntimeError("content 模式必须提供 --notebook-id 与 --source-id")

    headers = {"Content-Type": "application/json", "access-token": access_token}
    url = _build_api_url(base_url, f"/api/notebooks/{notebook_id}/sources/{source_id}/content")
    data = _request_json(url, headers=headers, timeout=60)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="NoteX Notebook 来源读取脚本 — 来源列表 / 正文获取"
    )
    parser.add_argument("--mode", required=True, choices=["list", "content"],
                        help="list=来源列表, content=获取正文")
    parser.add_argument("--notebook-id", default="", help="目标 Notebook ID")
    parser.add_argument("--source-id", default="", help="目标 Source ID（mode=content 必填）")
    parser.add_argument("--business-type", default="", help="业务类型筛选（mode=list 可选）")
    parser.add_argument("--base-url", default="",
                        help="生产地址（仅支持 https://notex.aishuo.co/noteX 或 /noteX/openapi）")
    parser.add_argument("--context-json", default="", help="鉴权上下文 JSON（可选，传给 cms-auth-skills）")
    args = parser.parse_args()

    try:
        base_url = _normalize_prod_base_url(args.base_url or PROD_NOTEX_BASE_URL)
        access_token = resolve_access_token(args.context_json)

        if args.mode == "list":
            list_sources(base_url, access_token, args.notebook_id, args.business_type)
        elif args.mode == "content":
            fetch_source_content(base_url, access_token, args.notebook_id, args.source_id)
    except RuntimeError as err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
