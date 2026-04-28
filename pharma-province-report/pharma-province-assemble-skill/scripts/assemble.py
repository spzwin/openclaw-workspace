#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
省级报告拼装脚本
按章节顺序读取所有 报告.md，拼接成含目录的完整报告。
每个章节报告内已内嵌独立参考文献，无需全局汇总。

用法:
  python assemble.py --province 广东省 --report-dir 省份报告/广东省
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

CHAPTER_ORDER = [
    ("1.1", "全省流行病学与疾病负担"),
    ("1.2", "全省患者地理分布与渠道结构"),
    ("1.3", "全省患者人口统计学特征"),
    ("1.4", "省级服务提供者总览"),
    ("2.1", "省级当前治疗格局"),
    ("2.2", "省级治疗渠道分布"),
    ("3.1", "省级竞争格局"),
    ("3.2", "省级产品准入政策"),
    ("3.3", "省级医保报销政策"),
    ("3.4", "省级费用结构与药品经济学"),
    ("4.1", "省级KOL识别"),
    ("4.2", "省级KOL分层管理"),
    ("5.1", "省级医疗体系概览"),
    ("5.2", "前10家重点医院逐院深度拆解"),
    ("6.1", "血液科"),
    ("6.2", "消化科"),
    ("6.3", "普外科骨科"),
    ("6.4", "妇产科"),
    ("6.5", "肾内科"),
    ("6.6", "心内科"),
]

# (anchor_id, display_text)
PART_HEADERS = {
    "1.1": ("part-1", "第一部分：省级市场全景"),
    "4.1": ("part-2", "第二部分：省级渠道深度与KOL"),
    "6.1": ("part-3", "第三部分：关键机构逐院深度拆解"),
}

# (anchor_id, display_text)
DIMENSION_HEADERS = {
    "1.1": ("dim-1", "维度一 全省市场机会与患者分布"),
    "2.1": ("dim-2", "维度二 省级治疗格局与渠道分布"),
    "3.1": ("dim-3", "维度三 省级竞争与准入策略"),
    "4.1": ("dim-4", "维度四 KOL识别与分层管理"),
    "5.1": ("dim-5", "维度五 省级医疗体系概览"),
    "6.1": ("dim-6", "维度六 关键机构逐院深度拆解（六大科室独立分析）"),
}


def find_chapter_dir(report_dir: Path, chapter_id: str) -> Path | None:
    for d in report_dir.iterdir():
        if d.is_dir() and d.name.startswith(chapter_id + "_"):
            return d
    return None


def chapter_anchor(chapter_id: str) -> str:
    return "ch-" + chapter_id.replace(".", "-")


def generate_toc(found_set: set) -> str:
    lines = ["## 目录", ""]

    current_dim = None

    for chapter_id, chapter_name in CHAPTER_ORDER:
        if chapter_id in PART_HEADERS:
            anchor_id, label = PART_HEADERS[chapter_id]
            lines.append(f"- **[{label}](#{anchor_id})**")

        if chapter_id in DIMENSION_HEADERS:
            anchor_id, label = DIMENSION_HEADERS[chapter_id]
            lines.append(f"  - **[{label}](#{anchor_id})**")
            current_dim = anchor_id

        status = "✅" if chapter_id in found_set else "❌"
        anchor = chapter_anchor(chapter_id)
        indent = "    " if current_dim else "  "
        lines.append(f"{indent}- {status} [{chapter_id} {chapter_name}](#{anchor})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="省级报告拼装脚本")
    parser.add_argument("--province", required=True, help="省份名称，如 广东省")
    parser.add_argument("--report-dir", required=True, help="报告目录路径")
    parser.add_argument("--output", help="输出文件路径（默认：报告目录/完整报告.md）")
    parser.add_argument("--product-a", default="莫诺菲", help="产品A名称")
    parser.add_argument("--product-b", default="科莫非", help="产品B名称")
    parser.add_argument("--product-a-generic", default="低分子量右旋糖酐铁注射液", help="产品A通用名")
    parser.add_argument("--product-b-generic", default="蔗糖铁注射液", help="产品B通用名")
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    if not report_dir.exists():
        print(f"❌ 报告目录不存在：{report_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else report_dir / "完整报告.md"

    sections = []
    missing = []
    found = []
    found_set = set()

    for chapter_id, chapter_name in CHAPTER_ORDER:
        chapter_dir = find_chapter_dir(report_dir, chapter_id)
        if chapter_dir is None:
            missing.append(f"{chapter_id} {chapter_name}")
            continue

        report_file = chapter_dir / "报告.md"
        if not report_file.exists():
            missing.append(f"{chapter_id} {chapter_name}（目录存在但缺少报告.md）")
            continue

        content = report_file.read_text(encoding="utf-8").strip()

        # 层级合规性校验：章节报告不应有一级或二级标题
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.rstrip()
            if stripped.startswith("# ") or stripped.startswith("## "):
                print(
                    f"⚠️  [{chapter_id}] 第{i}行存在疑似层级错误标题（应为###级）: "
                    f"{stripped[:70]}"
                )

        found.append((chapter_id, chapter_name))
        found_set.add(chapter_id)

        block_parts = []

        if chapter_id in PART_HEADERS:
            anchor_id, label = PART_HEADERS[chapter_id]
            block_parts.append(f'<a id="{anchor_id}"></a>\n\n## {label}')

        if chapter_id in DIMENSION_HEADERS:
            anchor_id, label = DIMENSION_HEADERS[chapter_id]
            block_parts.append(f'<a id="{anchor_id}"></a>\n\n## {label}')

        ch_anchor = chapter_anchor(chapter_id)
        block_parts.append(f'<a id="{ch_anchor}"></a>')
        block_parts.append(content)

        sections.append("\n\n".join(block_parts))

    if missing:
        print(f"⚠️  以下章节缺失（共 {len(missing)} 个），已跳过：")
        for m in missing:
            print(f"   ❌ {m}")

    toc = generate_toc(found_set)

    header = (
        f"# {args.province}\n\n"
        f"**产品组合**：{args.product_b}（{args.product_b_generic}）＋"
        f"{args.product_a}（{args.product_a_generic}）\n"
        f"**报告期间**：{datetime.now().strftime('%Y年%m月')}\n"
        f"**目标市场**：{args.province}\n"
        f"**面向对象**：省区经理与大区总监\n"
        f"**产品中心**：市场部\n"
        f"**报告生成日期**：{datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"---\n\n"
        f"> 康哲药业市场情报 · 仅供内部使用\n\n"
        f"---\n\n"
        f"## 执行摘要\n\n"
        f"> **本省疾病负担**：{{EXEC_IDA_BURDEN}}\n"
        f">\n"
        f"> **竞争格局**：{{EXEC_COMPETITION}}\n"
        f">\n"
        f"> **核心策略**：{{EXEC_STRATEGY}}\n\n"
        f"---\n\n"
        f"{toc}\n\n"
        f"---\n\n"
    )

    body = "\n\n---\n\n".join(sections)
    full_report = header + body + "\n"

    output_path.write_text(full_report, encoding="utf-8")
    print(
        f"✅ 完整报告已生成：{output_path}"
        f"（共 {len(found)}/20 章节，{len(full_report.splitlines())} 行）"
    )


if __name__ == "__main__":
    main()
