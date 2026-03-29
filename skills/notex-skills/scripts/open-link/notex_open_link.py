#!/usr/bin/env python3
"""
NoteX 链接补 token 并可选自动打开浏览器（可独立执行）

⚠️ 独立执行说明：
  本脚本可脱离 AI Agent 直接在命令行运行。
  执行前请先阅读 Open-Link 模块的 OpenAPI 接口文档获取完整入参说明：
  openapi/open-link/api-index.md

使用方式：
  # 生成带 token 的链接
  python3 notex-skills/scripts/open-link/notex_open_link.py

  # 自动打开浏览器（可选）
  python3 notex-skills/scripts/open-link/notex_open_link.py --auto-open

环境变量：
  XG_USER_TOKEN  — access-token（优先使用）
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.parse

PROD_NOTEX_HOST = "notex.aishuo.co"
DEFAULT_NOTEX_HOME_URL = "https://notex.aishuo.co/"


def _log(msg: str):
    print(msg, file=sys.stderr, flush=True)


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


# ──────────── URL 处理 ────────────

def _normalize_notex_url(raw_url: str) -> urllib.parse.SplitResult:
    parsed = urllib.parse.urlsplit(raw_url)
    if parsed.scheme != "https":
        raise RuntimeError("URL 必须使用 https 协议")
    if parsed.hostname != PROD_NOTEX_HOST:
        raise RuntimeError(f"URL 必须使用生产域名 {PROD_NOTEX_HOST}")
    pathname = parsed.path.rstrip("/") or "/"
    if pathname != "/":
        raise RuntimeError("URL 仅支持 NoteX 首页路由：https://notex.aishuo.co/")
    return parsed


def _build_authorized_url(raw_url: str, token: str) -> str:
    _normalize_notex_url(raw_url)
    return f"https://{PROD_NOTEX_HOST}/?token={urllib.parse.quote(token)}"


def _open_in_browser(url: str) -> bool:
    """尝试用系统默认浏览器打开 URL"""
    platform = sys.platform
    try:
        if platform == "darwin":
            subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform == "win32":
            subprocess.Popen(["cmd", "/c", "start", "", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="NoteX 链接补 token 并可选自动打开浏览器"
    )
    parser.add_argument("--url", default=DEFAULT_NOTEX_HOME_URL,
                        help="NoteX URL（仅支持首页 https://notex.aishuo.co/，默认即可）")
    parser.add_argument("--auto-open", action="store_true",
                        help="是否自动打开浏览器")
    parser.add_argument("--context-json", default="", help="鉴权上下文 JSON（可选，传给 cms-auth-skills）")
    args = parser.parse_args()

    try:
        access_token = resolve_access_token(args.context_json)
        final_url = _build_authorized_url(args.url, access_token)

        opened = False
        if args.auto_open:
            opened = _open_in_browser(final_url)

        _log(f"[open-link] 已生成可访问链接：{final_url}")
        if args.auto_open:
            _log("[open-link] 已尝试自动打开浏览器" if opened else "[open-link] 自动打开浏览器失败，请手动打开链接")

        output = {
            "url": final_url,
            "opened": opened,
            "authSource": "env" if os.environ.get("XG_USER_TOKEN", "").strip() else "cms-auth-skills",
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    except RuntimeError as err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
