#!/usr/bin/env python3
"""
NoteX 上下文沉淀与写入脚本（可独立执行）

功能：
1) 新建 Notebook 并写入首个 Source（可选标题与正文）
2) 向已有的 Notebook 追加新的 Source

⚠️ 独立执行说明：
  本脚本可脱离 AI Agent 直接在命令行运行。
  执行前请先阅读 Notebooks 模块的 OpenAPI 接口文档获取完整入参说明：
  openapi/notebooks/api-index.md

使用方式：
  # 新建笔记本并存入内容：
  python3 notex-skills/scripts/notebooks/notebooks_write.py --mode create --title "今日重点" --content "核心运营数据分析结论..."

  # 向现有笔记本追加内容：
  python3 notex-skills/scripts/notebooks/notebooks_write.py --mode append --notebook-id nb_xxx --title "补充资料" --content "细节1..."

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
                  body: dict = None, timeout: int = 60) -> dict:
    req_headers = dict(headers or {})
    req_data = None
    if body is not None:
        req_headers.setdefault("Content-Type", "application/json")
        req_data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"请求失败: {e.reason}") from e

    if not isinstance(payload, dict):
        return payload

    if "resultCode" in payload:
        if payload["resultCode"] != 1:
            raise RuntimeError(payload.get("resultMsg") or f"API error ({payload['resultCode']})")
        return payload.get("data", {})

    if "success" in payload:
        if not payload["success"]:
            raise RuntimeError(payload.get("error") or payload.get("message") or "API error (success=false)")
        return payload.get("data", payload)

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

def create_notebook(base_url: str, access_token: str, title: str, content: str):
    headers = {"Content-Type": "application/json", "access-token": access_token}
    _log("[create] 正在新建笔记本...")

    # 1. 创建 Notebook
    create_url = _build_api_url(base_url, "/api/notebooks")
    notebook_data = _request_json(create_url, method="POST", headers=headers,
                                  body={"title": title}, timeout=60)

    notebook_id = (notebook_data.get("id")
                   or notebook_data.get("notebookId")
                   or notebook_data.get("notebook_id"))
    if not notebook_id:
        raise RuntimeError("创建 Notebook 失败：响应中未返回 notebookId")

    _log("🎉 成功新建 Notebook！")
    _log(f"   Notebook ID: {notebook_id}")

    # 2. 如果有内容，写入首个 Source
    if content and notebook_id:
        _log("[create] 正在尝试将初始化内容存为源文件...")
        source_url = _build_api_url(base_url, f"/api/notebooks/{notebook_id}/sources")
        source_body = {
            "title": f"关于 {title} 的资料",
            "type": "text",
            "content_text": content,
        }
        source_data = _request_json(source_url, method="POST", headers=headers,
                                    body=source_body, timeout=60)
        source_id = source_data.get("sourceId") or source_data.get("id") or "未知"
        _log(f"✨ 成功存入预设笔记内容 (Source ID: {source_id})")


def append_source(base_url: str, access_token: str, notebook_id: str,
                  title: str, content: str):
    if not notebook_id:
        raise RuntimeError("追加模式 (--mode append) 必须提供 --notebook-id")

    headers = {"Content-Type": "application/json", "access-token": access_token}
    url = _build_api_url(base_url, f"/api/notebooks/{notebook_id}/sources")
    _log(f"[append] 正在向 Notebook ({notebook_id}) 追加来源...")

    body = {
        "title": title,
        "type": "text",
        "content_text": content,
    }

    data = _request_json(url, method="POST", headers=headers, body=body, timeout=60)
    source_id = data.get("id") or data.get("sourceId") or "未知"
    _log("🎉 成功追加 Source！")
    _log(f"   Source ID: {source_id}")


def main():
    parser = argparse.ArgumentParser(
        description="NoteX 上下文沉淀与写入脚本 — 创建笔记本 / 追加来源"
    )
    parser.add_argument("--mode", required=True, choices=["create", "append"],
                        help="create=新建笔记本, append=追加来源")
    parser.add_argument("--title", default="无标题笔记本", help="笔记本或来源标题")
    parser.add_argument("--content", default="", help="要保存的长文本内容")
    parser.add_argument("--notebook-id", default="", help="目标笔记本 ID（mode=append 时必填）")
    parser.add_argument("--base-url", default="",
                        help="生产地址（仅支持 https://notex.aishuo.co/noteX 或 /noteX/openapi）")
    parser.add_argument("--context-json", default="", help="鉴权上下文 JSON（可选，传给 cms-auth-skills）")
    args = parser.parse_args()

    try:
        base_url = _normalize_prod_base_url(args.base_url or PROD_NOTEX_BASE_URL)
        access_token = resolve_access_token(args.context_json)

        if args.mode == "create":
            create_notebook(base_url, access_token, args.title, args.content)
        elif args.mode == "append":
            append_source(base_url, access_token, args.notebook_id,
                          args.title, args.content)
    except RuntimeError as err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
