#!/usr/bin/env python3
"""
Skill 安装：通过 get-skills 接口拿到 downloadUrl，下载 ZIP 并解压到本地。

使用方式：
  python3 cms-find-skills/scripts/skill_registry/install_skill.py --code "cms-auth-skills"
  python3 cms-find-skills/scripts/skill_registry/install_skill.py --url "https://..."
  python3 cms-find-skills/scripts/skill_registry/install_skill.py --code "cms-auth-skills" --target /path/to/dir

说明：
  - 无需登录，无需授权
  - 安装来源固定为 Skill ZIP 压缩包
  - 默认安装到当前工作目录，可通过 --target 指定目录
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import ssl
import sys
import tempfile
import urllib.request
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def log(message: str, quiet: bool = False) -> None:
    if not quiet:
        print(message, file=sys.stderr)


def _resolve_skills_dir() -> str | None:
    """
    从脚本自身位置向上查找名为 'skills' 的祖先目录。
    不写死任何绝对路径，适用于任意 workspace（workspace / workspace-coder / workspace_xxx 等）。
    """
    current = os.path.dirname(os.path.abspath(__file__))
    while current != os.path.dirname(current):  # 没到根目录
        if os.path.basename(current) == "skills" and os.path.isdir(current):
            return current
        current = os.path.dirname(current)
    return None


def get_download_url_from_platform(code: str) -> str | None:
    """通过 get-skills 公开接口查询 downloadUrl。"""
    try:
        from get_skills import call_api, extract_skills, get_download_url

        result = call_api()
        skills = extract_skills(result)
        return get_download_url(skills, code)
    except Exception as exc:
        print(f"查询平台失败: {exc}", file=sys.stderr)
        return None


def download_file(url: str, dest_path: str, quiet: bool = False) -> bool:
    """下载 ZIP 到本地临时文件。"""
    log(f"正在下载: {url}", quiet)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            total = resp.headers.get("Content-Length")
            total = int(total) if total else None
            downloaded = 0
            with open(dest_path, "wb") as file_obj:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    file_obj.write(chunk)
                    downloaded += len(chunk)
                    if total and not quiet:
                        pct = downloaded * 100 // total
                        print(f"\r  进度: {pct}% ({downloaded}/{total})", end="", file=sys.stderr)
        if total and not quiet:
            print("", file=sys.stderr)
        log(f"下载完成: {dest_path}", quiet)
        return True
    except Exception as exc:
        print(f"下载失败: {exc}", file=sys.stderr)
        return False


def extract_zip(zip_path: str, target_dir: str, skill_code: str = "", quiet: bool = False) -> str | None:
    """
    解压 ZIP 到目标目录，返回最终安装目录。

    支持两种 ZIP 结构：
    1. ZIP 自带唯一顶层目录
    2. ZIP 文件散落在根目录，需要为其补一个 skill 目录
    """
    log(f"正在解压到: {target_dir}", quiet)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            names = zip_file.namelist()
            top_entries = {name.split("/")[0] for name in names if name.split("/")[0]}

            has_single_root = False
            root_name = ""
            if len(top_entries) == 1:
                root_name = next(iter(top_entries))
                has_single_root = all(
                    name == root_name or name.startswith(root_name + "/")
                    for name in names
                )

            if has_single_root:
                zip_file.extractall(target_dir)
                extracted = os.path.join(target_dir, root_name)
                log(f"解压完成: {extracted}", quiet)
                return extracted

            folder_name = skill_code or os.path.splitext(os.path.basename(zip_path))[0] or "skill"
            dest_dir = os.path.join(target_dir, folder_name)
            os.makedirs(dest_dir, exist_ok=True)
            zip_file.extractall(dest_dir)
            log(f"解压完成: {dest_dir}", quiet)
            return dest_dir
    except Exception as exc:
        print(f"解压失败: {exc}", file=sys.stderr)
        return None


def install_skill(
    code: str | None = None,
    url: str | None = None,
    target_dir: str | None = None,
    force: bool = False,
    quiet: bool = False,
) -> dict:
    """下载 ZIP 并安装 Skill 到本地目录。"""
    download_url = url or (get_download_url_from_platform(code) if code else None)
    if not download_url:
        return {
            "success": False,
            "message": f'无法获取 Skill "{code or ""}" 的下载地址，可能该 Skill 不存在或未发布',
        }

    target_dir = os.path.abspath(target_dir or _resolve_skills_dir() or os.getcwd())

    if code:
        existing = os.path.join(target_dir, code)
        if os.path.isdir(existing):
            if not force:
                log(f"已存在: {existing}（跳过，使用 --force 覆盖）", quiet)
                return {
                    "success": True,
                    "path": existing,
                    "message": f'Skill "{code}" 已存在于 {existing}',
                    "skipped": True,
                }
            log(f"覆盖: {existing}", quiet)
            shutil.rmtree(existing)

    with tempfile.TemporaryDirectory() as tmp_dir:
        filename = download_url.split("/")[-1].split("?")[0] or f"{code or 'skill'}.zip"
        if not filename.endswith(".zip"):
            filename = f"{code or 'skill'}.zip"
        tmp_file = os.path.join(tmp_dir, filename)

        if not download_file(download_url, tmp_file, quiet):
            return {"success": False, "message": "下载失败"}

        if not zipfile.is_zipfile(tmp_file):
            return {"success": False, "message": "下载结果不是 ZIP 压缩包"}

        installed_path = extract_zip(tmp_file, target_dir, skill_code=code or "", quiet=quiet)
        if not installed_path:
            return {"success": False, "message": "解压失败"}

        return {
            "success": True,
            "path": installed_path,
            "downloadUrl": download_url,
            "message": f"Skill 已安装到 {installed_path}",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill 安装：下载 ZIP 并解压到本地")
    parser.add_argument("--code", "-c", help="Skill code（通过 get-skills 查询 downloadUrl）")
    parser.add_argument("--url", "-u", help="直接提供 ZIP 下载地址")
    parser.add_argument("--target", "-t", help="安装目标目录，默认当前工作目录")
    parser.add_argument("--force", "-f", action="store_true", help="覆盖已存在的同名目录")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    args = parser.parse_args()

    if not args.code and not args.url:
        parser.error("需要 --code 或 --url 之一")

    result = install_skill(
        code=args.code,
        url=args.url,
        target_dir=args.target,
        force=args.force,
        quiet=args.quiet,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
