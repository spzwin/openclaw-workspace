#!/usr/bin/env python3
"""
Skill 发现：浏览、搜索、查看详情、获取下载地址。

主要调用接口：
  GET https://sg-cwork-api.mediportal.com.cn/im/skill/nologin/list

使用方式：
  python3 cms-find-skills/scripts/skill_registry/get_skills.py
  python3 cms-find-skills/scripts/skill_registry/get_skills.py --search "机器人"
  python3 cms-find-skills/scripts/skill_registry/get_skills.py --detail "cms-auth-skills"
  python3 cms-find-skills/scripts/skill_registry/get_skills.py --url "cms-auth-skills"

说明：
  - 这是 nologin 接口，不需要任何授权
  - install_skill.py 会复用这里的 downloadUrl 查询逻辑
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.request

API_URL = "https://sg-cwork-api.mediportal.com.cn/im/skill/nologin/list"


def call_api() -> dict:
    """调用平台公开 Skill 列表接口。"""
    req = urllib.request.Request(
        API_URL,
        headers={"Content-Type": "application/json"},
        method="GET",
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_skills(result: dict) -> list[dict]:
    """从响应中提取 Skill 列表。"""
    if isinstance(result, list):
        return result
    return result.get("data") or result.get("resultData") or []


def search_skills(skills: list[dict], keyword: str) -> list[dict]:
    """按名称、描述、code、label 模糊匹配。"""
    kw = keyword.lower()
    return [
        skill
        for skill in skills
        if kw in (skill.get("name") or "").lower()
        or kw in (skill.get("description") or "").lower()
        or kw in (skill.get("code") or "").lower()
        or kw in (skill.get("label") or "").lower()
    ]


def find_one(skills: list[dict], query: str) -> dict | None:
    """按 code 或 name 查找单个 Skill。"""
    q = query.lower()

    for skill in skills:
        if (skill.get("code") or "").lower() == q:
            return skill

    for skill in skills:
        if (skill.get("name") or "").lower() == q:
            return skill

    for skill in skills:
        if q in (skill.get("code") or "").lower() or q in (skill.get("name") or "").lower():
            return skill

    return None


def get_download_url(skills: list[dict], query: str) -> str | None:
    """按 code 或 name 获取下载地址。"""
    skill = find_one(skills, query)
    if not skill:
        return None
    return skill.get("downloadUrl")


def format_list(skills: list[dict]) -> str:
    """以紧凑表格格式展示列表。"""
    if not skills:
        return "（暂无已发布的 Skill）"

    lines = [
        f"{'#':<4} {'名称':<24} {'Code':<24} {'版本':<6} {'是否内置':<8} {'描述'}",
        "-" * 110,
    ]
    for index, skill in enumerate(skills, 1):
        name = (skill.get("name") or "")[:22]
        code = (skill.get("code") or "")[:22]
        version = str(skill.get("version", ""))[:5]
        internal = "是" if skill.get("isInternal") else "否"
        desc = (skill.get("description") or "")[:40]
        lines.append(f"{index:<4} {name:<24} {code:<24} {version:<6} {internal:<8} {desc}")
    lines.append(f"\n共 {len(skills)} 个 Skill")
    return "\n".join(lines)


def format_detail(skill: dict) -> str:
    """格式化单个 Skill 的详情。"""
    owner = skill.get("owner") or {}
    lines = [
        "=" * 72,
        f"名称: {skill.get('name', '-')}",
        f"Code: {skill.get('code', '-')}",
        f"ID: {skill.get('id', '-')}",
        f"版本: {skill.get('version', '-')}",
        f"标签: {skill.get('label') or '-'}",
        f"描述: {skill.get('description') or '-'}",
        f"下载地址: {skill.get('downloadUrl') or '-'}",
        f"作者: {owner.get('name', '-')}",
        f"创建时间: {skill.get('createTime', '-')}",
        f"下载数: {skill.get('downloadCount', '-')}",
        f"点赞数: {skill.get('likeCount', '-')}",
        f"收藏数: {skill.get('favoriteCount', '-')}",
        f"内置 Skill: {'是' if skill.get('isInternal') else '否'}",
        "=" * 72,
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill 发现：浏览、搜索、详情、下载地址")
    parser.add_argument("--search", "-s", help="按关键词搜索 Skill")
    parser.add_argument("--detail", "-d", help="查看某个 Skill 详情")
    parser.add_argument(
        "--url",
        "--download-url",
        "-u",
        dest="url",
        help="仅输出某个 Skill 的 downloadUrl",
    )
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    try:
        result = call_api()
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    skills = extract_skills(result)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.url:
        url = get_download_url(skills, args.url)
        if not url:
            print(f"未找到 \"{args.url}\" 的下载地址", file=sys.stderr)
            sys.exit(1)
        print(url)
        return

    if args.detail:
        skill = find_one(skills, args.detail)
        if not skill:
            print(f"未找到匹配 \"{args.detail}\" 的 Skill", file=sys.stderr)
            sys.exit(1)
        print(format_detail(skill))
        return

    if args.search:
        matched = search_skills(skills, args.search)
        if not matched:
            print(f"搜索 \"{args.search}\" 无结果", file=sys.stderr)
            sys.exit(1)
        print(f"搜索 \"{args.search}\" 匹配到 {len(matched)} 个结果：\n")
        print(format_list(matched))
        return

    print("平台 Skill 列表\n")
    print(format_list(skills))


if __name__ == "__main__":
    main()
