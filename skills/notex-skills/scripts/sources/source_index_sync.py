#!/usr/bin/env python3
"""
Notebook/Source 索引同步脚本（可独立执行）

功能：
1) 全量拉取索引树并落盘（覆盖写，保证全量刷新）
2) 按 notebookId/sourceId 拉取来源最小详情（ID + 名称）并落盘
3) 可配置定时轮询，持续全量刷新索引

⚠️ 独立执行说明：
  本脚本可脱离 AI Agent 直接在命令行运行。
  执行前请先阅读 Sources 模块的 OpenAPI 接口文档获取完整入参说明：
  openapi/sources/api-index.md

使用方式：
  python3 notex-skills/scripts/sources/source_index_sync.py --mode index
  python3 notex-skills/scripts/sources/source_index_sync.py --mode detail --notebook-id nb_xxx
  python3 notex-skills/scripts/sources/source_index_sync.py --mode detail --source-id src_xxx
  python3 notex-skills/scripts/sources/source_index_sync.py --mode index --interval-minutes 60

环境变量：
  XG_USER_TOKEN  — access-token（优先使用）
"""

import argparse
import hashlib
import json
import os
import ssl
import subprocess
import sys
import time
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

    if isinstance(payload, dict) and "resultCode" in payload:
        if payload["resultCode"] != 1:
            raise RuntimeError(payload.get("resultMsg") or f"API error ({payload['resultCode']})")
        return payload.get("data", {})

    return payload


def _write_json(file_path: str, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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


def _get_cache_user_id(token: str) -> str:
    if not token:
        return "unknown"
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]
    return f"token-{digest}"


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


# ──────────── 统计工具 ────────────

def _collect_tree_stats(tree) -> dict:
    notebook_count = 0
    source_count = 0

    def walk(nodes):
        nonlocal notebook_count, source_count
        if not isinstance(nodes, list):
            return
        for node in nodes:
            notebook_count += 1
            sources = node.get("sources", [])
            source_count += len(sources) if isinstance(sources, list) else 0
            walk(node.get("children", []))

    walk(tree)
    return {"notebookCount": notebook_count, "sourceCount": source_count}


# ──────────── 业务功能 ────────────

def refresh_index_once(base_url: str, access_token: str, index_type: str,
                       cache_dir: str, output_path: str):
    valid_types = {"all", "owned", "collaborated"}
    if index_type not in valid_types:
        raise RuntimeError(f"非法 type: {index_type}（仅支持 all | owned | collaborated）")

    headers = {"Content-Type": "application/json", "access-token": access_token}
    url = _build_api_url(base_url,
                         f"/api/notebooks/sources/index-tree?type={urllib.parse.quote(index_type)}")
    data = _request_json(url, headers=headers, timeout=120)

    if not output_path:
        user_id = _get_cache_user_id(access_token)
        output_path = os.path.join(cache_dir, user_id, "index-tree.json")

    _write_json(output_path, data)
    tree = data.get("tree", [])
    stats = _collect_tree_stats(tree)
    generated_at = data.get("generatedAt", "")
    _log(f"[index] 全量刷新完成: {output_path}")
    _log(f"[index] notebooks={stats['notebookCount']}, sources={stats['sourceCount']}, generatedAt={generated_at}")


def fetch_details_once(base_url: str, access_token: str, notebook_id: str,
                       source_id: str, cache_dir: str, output_path: str):
    if not notebook_id and not source_id:
        raise RuntimeError("detail 模式必须提供 --notebook-id 或 --source-id")

    headers = {"Content-Type": "application/json", "access-token": access_token}

    query_parts = []
    if notebook_id:
        query_parts.append(f"notebookId={urllib.parse.quote(notebook_id)}")
    if source_id:
        query_parts.append(f"sourceId={urllib.parse.quote(source_id)}")
    query_str = "&".join(query_parts)

    url = _build_api_url(base_url, f"/api/notebooks/sources/details?{query_str}")
    data = _request_json(url, headers=headers, timeout=120)

    if not output_path:
        user_id = _get_cache_user_id(access_token)
        default_file = f"source-{source_id}.json" if source_id else f"notebook-{notebook_id}.json"
        output_path = os.path.join(cache_dir, user_id, "details", default_file)

    _write_json(output_path, data)
    mode = data.get("mode", "")
    nb = data.get("notebook", {})
    nb_id = nb.get("id", "-") if isinstance(nb, dict) else "-"
    _log(f"[detail] 最小详情已写入: {output_path}")
    _log(f"[detail] mode={mode}, notebook={nb_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Notebook/Source 索引同步脚本 — 全量索引树 / 详情查询"
    )
    parser.add_argument("--mode", default="index", choices=["index", "detail"],
                        help="index=全量索引, detail=详情查询")
    parser.add_argument("--type", default="all", help="index 模式下的可见范围: all | owned | collaborated")
    parser.add_argument("--notebook-id", default="", help="目标 Notebook ID（mode=detail）")
    parser.add_argument("--source-id", default="", help="目标 Source ID（mode=detail）")
    parser.add_argument("--base-url", default="",
                        help="生产地址（仅支持 https://notex.aishuo.co/noteX 或 /noteX/openapi）")
    parser.add_argument("--cache-dir", default="",
                        help="本地缓存根目录（默认: ../../cache/notebook-source-index）")
    parser.add_argument("--output", default="", help="指定输出文件")
    parser.add_argument("--interval-minutes", type=int, default=0,
                        help="仅 index 模式生效，按分钟持续全量刷新")
    parser.add_argument("--context-json", default="", help="鉴权上下文 JSON（可选，传给 cms-auth-skills）")
    args = parser.parse_args()

    try:
        base_url = _normalize_prod_base_url(args.base_url or PROD_NOTEX_BASE_URL)
        access_token = resolve_access_token(args.context_json)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_cache = args.cache_dir or os.path.join(script_dir, "..", "..",
                                                        "cache", "notebook-source-index")
        cache_dir = os.path.abspath(default_cache)

        if args.mode == "index":
            if args.interval_minutes <= 0:
                refresh_index_once(base_url, access_token, args.type, cache_dir, args.output)
            else:
                interval_s = args.interval_minutes * 60
                _log(f"[index] 已进入定时全量刷新模式，每 {args.interval_minutes} 分钟执行一次")
                while True:
                    try:
                        refresh_index_once(base_url, access_token, args.type, cache_dir, args.output)
                    except RuntimeError as e:
                        _log(f"[index] 刷新失败: {e}")
                    time.sleep(interval_s)

        elif args.mode == "detail":
            fetch_details_once(base_url, access_token, args.notebook_id,
                               args.source_id, cache_dir, args.output)

    except RuntimeError as err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
