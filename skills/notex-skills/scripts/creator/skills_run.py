#!/usr/bin/env python3
"""
NoteX Skills 通用脚本（可独立执行）

支持 9 种能力：slide / mindmap / report / flashcards / quiz / infographic / audio / video / ops-chat

⚠️ 独立执行说明：
  本脚本可脱离 AI Agent 直接在命令行运行。
  执行前请先阅读对应模块的 OpenAPI 接口文档获取完整入参说明：
  - 创作类（slide/mindmap/report 等）：openapi/creator/api-index.md
  - 运营问答（ops-chat）：openapi/ops/api-index.md

使用方式：
  python3 notex-skills/scripts/creator/skills_run.py --skill <技能> --title "标题" --content "内容"
  # 需设置环境变量 XG_USER_TOKEN，或已安装 cms-auth-skills 并可通过 --context-json 传入鉴权参数

示例：
  python3 notex-skills/scripts/creator/skills_run.py --skill mindmap --title "口腔AI趋势" --content "主要数据..."
  python3 notex-skills/scripts/creator/skills_run.py --skill slide   --title "年度汇报"   --content "销售数据..."
  python3 notex-skills/scripts/creator/skills_run.py --skill quiz    --title "护理测验"   --content "护理规范..."
  python3 notex-skills/scripts/creator/skills_run.py --skill ops-chat --content "查询活跃用户排名"

环境变量：
  XG_USER_TOKEN  — access-token（优先使用）
"""

import argparse
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ===================== 配置 =====================
NOTEX_BASE_URL = "https://notex.aishuo.co/noteX"
POLL_INTERVAL_S = 60        # 每 60 秒轮询一次
POLL_MAX_TIMES = 20         # 最多 20 次（20 分钟上限）

# 各技能的预计生成时间（仅用于输出提示）
SKILL_INFO = {
    "slide":       {"name": "演示文稿（PPT）", "time": "3~5 分钟"},
    "mindmap":     {"name": "思维导图",         "time": "1~2 分钟"},
    "report":      {"name": "分析报告",         "time": "1~3 分钟"},
    "flashcards":  {"name": "记忆卡片",         "time": "1~2 分钟"},
    "quiz":        {"name": "测验题目",         "time": "1~2 分钟"},
    "infographic": {"name": "信息图",           "time": "2~4 分钟"},
    "audio":       {"name": "音频播客",         "time": "3~6 分钟"},
    "video":       {"name": "视频",             "time": "5~10 分钟"},
    "ops-chat":    {"name": "OPS 运营智能助理", "time": "即时 (内含大模型运算, 最长5分钟)"},
}

ALLOWED_SKILLS = list(SKILL_INFO.keys())
# ================================================


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def _request_json(url: str, *, method: str = "GET", headers: dict = None,
                  body: dict = None, timeout: int = 60) -> dict:
    """发起 HTTP 请求并返回 JSON。"""
    req_headers = dict(headers or {})
    req_data = None
    if body is not None:
        req_headers.setdefault("Content-Type", "application/json")
        req_data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"请求失败: {e.reason}") from e


def _validate_prod_url(raw_url: str, expected_host: str, label: str) -> str:
    parsed = urllib.parse.urlsplit(raw_url)
    if parsed.scheme != "https":
        raise RuntimeError(f"{label} 必须使用 https 协议")
    if parsed.hostname != expected_host:
        raise RuntimeError(f"{label} 必须使用生产域名 {expected_host}")
    return f"{parsed.scheme}://{parsed.hostname}{parsed.path.rstrip('/')}"


def _build_notex_api_url(base_url: str, api_path: str) -> str:
    normalized = api_path if api_path.startswith("/openapi/") else f"/openapi{api_path.replace('/api', '', 1)}"
    if base_url.endswith("/openapi"):
        return f"{base_url}{normalized.replace('/openapi', '', 1)}"
    if base_url.endswith("/noteX"):
        return f"{base_url}{normalized}"
    raise RuntimeError("notexBaseUrl 路径必须是 /noteX 或 /noteX/openapi")


# ──────────── 鉴权：统一由 cms-auth-skills 提供 ────────────

def _find_login_py() -> str:
    """定位 cms-auth-skills/scripts/auth/login.py"""
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
    """
    统一鉴权解析：
    1. 优先从环境变量 XG_USER_TOKEN 读取
    2. 否则调用 cms-auth-skills/scripts/auth/login.py --ensure
    """
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


# ──────────── 创作任务 ────────────

def create_task(xg_token: str, skill: str, title: str, content: str,
                require_text: str = "") -> str:
    """Step 2: 提交技能生成任务"""
    info = SKILL_INFO[skill]
    _log(f"\n[Step 2] 提交「{info['name']}」生成任务...")

    biz_id = f"skills_{skill}_{int(time.time() * 1000)}"
    body = {
        "title": title,
        "bizId": biz_id,
        "bizType": "TRILATERA_SKILLS",
        "skills": [skill],
        "require": require_text or f"请根据提供的内容生成{info['name']}，主题为：{title}",
        "sources": [{"id": "src_001", "title": f"{title} - 素材", "content_text": content}],
    }

    url = _build_notex_api_url(NOTEX_BASE_URL, "/openapi/trilateral/autoTask")
    data = _request_json(url, method="POST", headers={
        "Content-Type": "application/json",
        "access-token": xg_token,
    }, body=body)

    if data.get("resultCode") != 1:
        raise RuntimeError(f"创建任务失败: {data.get('resultMsg')}")

    task_ids = data.get("data", {}).get("taskId", [])
    task_id = task_ids[0] if isinstance(task_ids, list) and task_ids else task_ids
    notebook_id = data.get("data", {}).get("noteBook_id", "")
    _log(f"✅ 任务创建成功")
    _log(f"   taskId:     {task_id}")
    _log(f"   notebookId: {notebook_id}")
    return task_id


def poll_task_status(task_id: str, xg_token: str, skill_name: str) -> str:
    """Step 3: 轮询任务状态"""
    _log(f"\n[Step 3] 轮询任务状态（每 {POLL_INTERVAL_S}s，最多 {POLL_MAX_TIMES} 次 = {POLL_MAX_TIMES} 分钟上限）...")

    url = _build_notex_api_url(NOTEX_BASE_URL, f"/openapi/trilateral/taskStatus/{task_id}")

    for i in range(1, POLL_MAX_TIMES + 1):
        # 第一次等 3 秒，后续等完整间隔
        time.sleep(3 if i == 1 else POLL_INTERVAL_S)

        data = _request_json(url, method="GET", headers={"access-token": xg_token})
        task_data = data.get("data", {})
        task_status = task_data.get("task_status", "")
        task_url = task_data.get("url", "")

        _log(f"   第 {i} 次轮询 → task_status: {task_status}")

        if task_status == "COMPLETED" and task_url:
            final_url = f"{task_url}&token={xg_token}"
            _log(f"\n🎉 {skill_name}生成完成！")
            _log(f"   查看链接：{final_url}")
            return final_url

        if task_status == "FAILED":
            raise RuntimeError(f"{skill_name}生成失败，请检查输入内容后重试")

    raise RuntimeError(f"轮询超时（超过 {POLL_MAX_TIMES} 分钟），请稍后通过 taskId 查询状态")


def call_ops_chat(xg_token: str, message: str, timeout_ms: int = 300000) -> None:
    """Step 2.B: OPS 运营问答"""
    if not message:
        raise RuntimeError("ops-chat 需要提供提问内容 (--content)")

    timeout_s = timeout_ms // 1000
    _log(f"\n[Step 2] 请求 OPS 智能聊天 (自动最长等待 {timeout_s // 60} 分钟)...")

    url = _build_notex_api_url(NOTEX_BASE_URL, "/openapi/ops/ai-chat")
    body = {"message": message}

    data = _request_json(url, method="POST", headers={
        "Content-Type": "application/json",
        "access-token": xg_token,
    }, body=body, timeout=timeout_s)

    if data.get("error"):
        raise RuntimeError(f"OPS 服务器错误: {data['error']}")

    _log("\n🎉 回答生成完毕：\n")
    print(data.get("reply", ""))

    history_count = data.get("historyCount")
    if history_count is not None:
        _log(f"\n(当前记录历史上下文数: {history_count} 对)")


# ──────────── 主流程 ────────────

def main():
    parser = argparse.ArgumentParser(
        description="NoteX Skills 通用脚本 — 支持创作任务与 OPS 运营问答"
    )
    parser.add_argument("--skill", required=True, choices=ALLOWED_SKILLS,
                        help=f"技能类型: {' | '.join(ALLOWED_SKILLS)}")
    parser.add_argument("--title", default="", help="标题（创作类必填）")
    parser.add_argument("--content", default="", help="素材内容 / ops-chat 问题")
    parser.add_argument("--require", default="", help="生成要求/风格（可选）")
    parser.add_argument("--context-json", default="", help="鉴权上下文 JSON（可选，传给 cms-auth-skills）")
    args = parser.parse_args()

    # 参数校验
    if args.skill == "ops-chat":
        if not args.content and not args.title:
            print("❌ ops-chat 请提供问题内容：--content \"问题\"（或使用 --title）", file=sys.stderr)
            sys.exit(1)
    else:
        if not args.title:
            print("❌ 请提供标题：--title \"标题\"", file=sys.stderr)
            sys.exit(1)
        if not args.content:
            print("❌ 请提供素材内容：--content \"内容\"", file=sys.stderr)
            sys.exit(1)

    # 验证生产 URL
    _validate_prod_url(NOTEX_BASE_URL, "notex.aishuo.co", "notexBaseUrl")

    info = SKILL_INFO[args.skill]
    _log(f"\n🚀 NoteX Skills — {info['name']}")
    _log(f"   预计生成时间：{info['time']}")
    _log(f"   标题：{args.title}")

    try:
        xg_token = resolve_access_token(args.context_json)

        if args.skill == "ops-chat":
            call_ops_chat(xg_token, args.content or args.title)
        else:
            task_id = create_task(xg_token, args.skill, args.title, args.content, args.require)
            poll_task_status(task_id, xg_token, info["name"])
    except RuntimeError as err:
        print(f"\n❌ 错误：{err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
