#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医院基础数据 CLI 查询工具

原则：
1. 原始 Excel 是唯一事实源。
2. CLI 是唯一计算入口。
3. 报告中的关键数字必须来自 CLI 输出。

依赖：pandas, openpyxl
安装：pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCEL = ROOT / "references" / "hospital_base.xlsx"
DEFAULT_SCHEMA = ROOT / "references" / "schema.json"
DEFAULT_PRODUCT_MAPPING = ROOT / "references" / "product_mapping.json"
COMMAND_NAMES = {
    "validate",
    "list-values",
    "summary",
    "group",
    "rank",
    "product-compare",
    "detail",
    "hospital",
    "opportunity",
}
GLOBAL_ARGS_WITH_VALUE = {
    "--excel",
    "--sheet",
    "--format",
    "--output",
    "--query-id",
    "--query-output-dir",
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_value(v: Any) -> Any:
    if pd.isna(v):
        return ""
    if isinstance(v, str):
        return v.strip()
    return v


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def json_default(obj: Any) -> Any:
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    try:
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
    except Exception:
        pass
    return str(obj)


def normalize_global_args(argv: List[str]) -> List[str]:
    """Allow global options to appear after the subcommand.

    argparse requires root-level options to appear before the subcommand.
    The province workflow may append `--query-id` / `--query-output-dir`
    later, so normalize the argv order before parsing.
    """

    if not argv:
        return argv

    command_idx = None
    for idx, token in enumerate(argv):
        if token in COMMAND_NAMES:
            command_idx = idx
            break
    if command_idx is None:
        return argv

    prefix = list(argv[:command_idx])
    command = argv[command_idx]
    suffix = list(argv[command_idx + 1 :])
    globals_after: List[str] = []
    command_args: List[str] = []
    idx = 0
    while idx < len(suffix):
        token = suffix[idx]
        if token in GLOBAL_ARGS_WITH_VALUE:
            globals_after.append(token)
            if idx + 1 < len(suffix):
                globals_after.append(suffix[idx + 1])
                idx += 2
                continue
        command_args.append(token)
        idx += 1
    return prefix + globals_after + [command] + command_args


class DataCLI:
    def __init__(self, excel_path: Path, sheet_name: Optional[str] = None):
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self.schema = load_json(DEFAULT_SCHEMA)
        raw_mapping = load_json(DEFAULT_PRODUCT_MAPPING)["products"]
        # 规范化 product_mapping 中的 flow_column：
        # 去除首尾空白 + 删除内嵌换行符，与 _prepare_df() 对列名的处理保持一致，
        # 使 Excel 列名无论是否含换行都能与 product_mapping 匹配。
        self.product_mapping = {
            product: {
                **conf,
                "flow_column": str(conf["flow_column"]).strip().replace("\n", "").replace("\r", ""),
            }
            for product, conf in raw_mapping.items()
        }
        self.aliases = self.schema.get("aliases", {})
        self.df = self._load_excel()
        self._prepare_df()

    def _load_excel(self) -> pd.DataFrame:
        if not self.excel_path.exists():
            raise FileNotFoundError(f"找不到 Excel 文件：{self.excel_path}")
        if self.sheet_name:
            return pd.read_excel(self.excel_path, sheet_name=self.sheet_name, engine="openpyxl")
        return pd.read_excel(self.excel_path, engine="openpyxl")

    def _prepare_df(self) -> None:
        # 清理列名：去除首尾空白 + 替换列名内嵌的换行符（Excel 表头换行常见问题）
        self.df.columns = [
            str(c).strip().replace("\n", "").replace("\r", "")
            for c in self.df.columns
        ]
        for col in self.df.columns:
            if self.df[col].dtype == "object":
                self.df[col] = self.df[col].map(normalize_value)
        # 兼容旧列名"潜力量"：若 Excel 仍用旧表头，自动重命名为"IDA患者数"
        if "IDA患者数" in self.df.columns:
            self.df["IDA患者数"] = to_number(self.df["IDA患者数"])
        elif "潜力量" in self.df.columns:
            self.df.rename(columns={"潜力量": "IDA患者数"}, inplace=True)
            self.df["IDA患者数"] = to_number(self.df["IDA患者数"])
        # 兼容 flow_column_aliases：若 Excel 使用简短列名（如"莫诺菲"/"科莫非"）
        # 或含换行的列名，自动重命名为规范列名，确保后续计算一致。
        for product, conf in self.product_mapping.items():
            canonical = conf["flow_column"]
            if canonical not in self.df.columns:
                for alias in conf.get("flow_column_aliases", []):
                    alias_norm = str(alias).strip().replace("\n", "").replace("\r", "")
                    if alias_norm in self.df.columns:
                        self.df.rename(columns={alias_norm: canonical}, inplace=True)
                        break

        for product, conf in self.product_mapping.items():
            col = conf["flow_column"]
            if col in self.df.columns:
                self.df[col] = to_number(self.df[col])
                # 增加短别名列，便于内部统一计算
                self.df[f"{product}流向"] = self.df[col]

    # ------------------------------------------------------------------
    # 容错辅助方法
    # ------------------------------------------------------------------

    def _warn(self, message: str) -> None:
        """向 stderr 输出 JSON 格式警告，不影响 stdout 的正常 JSON 结果。"""
        print(json.dumps({"level": "warning", "message": message}, ensure_ascii=False), file=sys.stderr)

    def _suggest_column(self, field: str, columns: List[str]) -> Optional[str]:
        """尝试从 columns 中找出与 field 最相近的列名。
        匹配顺序：精确 > 大小写不敏感 > field 是列名子串 > 列名是 field 子串。
        """
        if field in columns:
            return field
        field_lower = field.lower()
        col_lower = {c.lower(): c for c in columns}
        if field_lower in col_lower:
            return col_lower[field_lower]
        for c in columns:
            if field in c:
                return c
        for c in columns:
            if c in field:
                return c
        return None

    def resolve_field(self, field: str) -> str:
        """解析字段别名。
        先查 schema aliases（精确），再尝试大小写不敏感别名匹配，最后原样返回。
        """
        field = field.strip()
        if field in self.aliases:
            return self.aliases[field]
        field_lower = field.lower()
        for k, v in self.aliases.items():
            if k.lower() == field_lower:
                return v
        return field

    def product_flow_col(self, product: str) -> str:
        """返回产品对应的 DataFrame 列名。产品或列名不存在时抛出含上下文的 ValueError。"""
        if product not in self.product_mapping:
            raise ValueError(
                f"未知产品：{product}。可选产品：{list(self.product_mapping.keys())}"
            )
        col = self.product_mapping[product]["flow_column"]
        if col not in self.df.columns:
            # 列出当前 DataFrame 里所有含产品名或"流向"的列，辅助排查
            candidates = [c for c in self.df.columns if product in c or "流向" in c]
            hint = f"；当前数据集中含相关字样的列：{candidates}" if candidates else ""
            raise ValueError(
                f"产品 {product} 对应字段 [{col}] 在数据集中不存在{hint}。"
                f"已加载列：{list(self.df.columns)}"
            )
        return col

    def apply_filters(self, df: pd.DataFrame, args: argparse.Namespace) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        filters: Dict[str, Any] = {}
        filter_map = {
            "大区": getattr(args, "大区", None),
            "区域": getattr(args, "区域", None),
            "省": getattr(args, "省", None),
            "市": getattr(args, "市", None),
            "区/县": getattr(args, "区县", None),
            "客户名称": getattr(args, "客户名称", None),
            "客户性质": getattr(args, "客户性质", None),
            "类型名称": getattr(args, "类型名称", None),
            "客户级别": getattr(args, "客户级别", None),
            "医院级别-大类": getattr(args, "医院级别大类", None),
        }
        out = df.copy()
        fuzzy_flag = bool(getattr(args, "fuzzy", False))
        for col, val in filter_map.items():
            if val is None or val == "":
                continue
            if col not in out.columns:
                # 容错：筛选列缺失时发出警告并跳过，不崩溃
                # 先尝试在实际列名中找到近似列
                suggestion = self._suggest_column(col, list(out.columns))
                hint = f"，最相近列：[{suggestion}]" if suggestion else ""
                self._warn(f"筛选字段 [{col}] 在数据集中不存在{hint}，已跳过该筛选条件")
                continue
            filters[col] = val
            # 模糊匹配语义：仅在显式 --fuzzy 时启用，且只对文本主键（客户名称）启用
            # 其它字段（省/市/区县/级别）始终精确匹配，避免 "广西" 误命中其它含字
            if fuzzy_flag and col == "客户名称":
                out = out[out[col].astype(str).str.contains(str(val), na=False, regex=False)]
            else:
                out = out[out[col].astype(str) == str(val)]

        min_potential = getattr(args, "min_potential", None)
        max_potential = getattr(args, "max_potential", None)
        if "IDA患者数" in out.columns:
            if min_potential is not None:
                out = out[out["IDA患者数"] >= min_potential]
                filters["min_potential"] = min_potential
            if max_potential is not None:
                out = out[out["IDA患者数"] <= max_potential]
                filters["max_potential"] = max_potential
        elif min_potential is not None or max_potential is not None:
            self._warn("IDA患者数 列不存在，--min-potential / --max-potential 筛选已跳过")

        product = getattr(args, "产品", None)
        flow_status = getattr(args, "flow_status", None)
        min_flow = getattr(args, "min_flow", None)
        max_flow = getattr(args, "max_flow", None)
        if product:
            col = self.product_flow_col(product)
            filters["产品"] = product
            if flow_status:
                filters["flow_status"] = flow_status
                if flow_status == "covered":
                    out = out[out[col] > 0]
                elif flow_status == "uncovered":
                    out = out[out[col] == 0]
                elif flow_status == "returned":
                    out = out[out[col] < 0]
                elif flow_status == "not-covered":
                    out = out[out[col] <= 0]
                else:
                    raise ValueError("--flow-status 只能是 covered / uncovered / returned / not-covered")
            if min_flow is not None:
                out = out[out[col] >= min_flow]
                filters["min_flow"] = min_flow
            if max_flow is not None:
                out = out[out[col] <= max_flow]
                filters["max_flow"] = max_flow
        elif flow_status or min_flow is not None or max_flow is not None:
            raise ValueError("使用 --flow-status / --min-flow / --max-flow 时必须指定 --产品")

        return out, filters

    def meta(self, command: str, before: int, after: int) -> Dict[str, Any]:
        return {
            "source_file": str(self.excel_path),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command,
            "row_count_before_filter": before,
            "row_count_after_filter": after,
        }

    def calc_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        hospital_count = int(len(df))
        total_potential = float(to_number(df.get("IDA患者数", pd.Series(dtype=float))).sum())
        products = {}
        for product, conf in self.product_mapping.items():
            col = conf["flow_column"]
            if col not in df.columns:
                products[product] = {"error": f"字段不存在：{col}"}
                continue
            flow = to_number(df[col])
            total_flow = float(flow.sum())
            covered = int((flow > 0).sum())
            returned = int((flow < 0).sum())
            uncovered = int((flow == 0).sum())
            products[product] = {
                "spec": conf.get("spec"),
                "period": conf.get("period"),
                "total_flow": total_flow,
                "covered_hospital_count": covered,
                "returned_hospital_count": returned,
                "uncovered_hospital_count": uncovered,
                "coverage_rate": None if hospital_count == 0 else covered / hospital_count,
                "potential_conversion_rate": None if total_potential == 0 else total_flow / total_potential,
            }
        return {
            "hospital_count": hospital_count,
            "total_potential": total_potential,
            "products": products,
        }

    def cmd_validate(self) -> Dict[str, Any]:
        required = list(self.schema.get("required_columns", []))
        required += [conf["flow_column"] for conf in self.product_mapping.values()]
        missing = [c for c in required if c not in self.df.columns]
        null_check = {}
        for c in ["省", "市", "区/县", "客户名称", "IDA患者数"]:
            if c in self.df.columns:
                null_check[c] = int(self.df[c].isna().sum() + (self.df[c].astype(str).str.strip() == "").sum())
        numeric_check = {}
        for c in ["IDA患者数"] + [conf["flow_column"] for conf in self.product_mapping.values()]:
            if c not in self.df.columns:
                continue
            try:
                # 按规范列名直接读取原始 Excel（未经别名归一化）
                raw = pd.read_excel(self.excel_path, engine="openpyxl", usecols=[c])
                numeric_check[c] = {
                    "non_numeric_count": int(
                        pd.to_numeric(raw[c], errors="coerce").isna().sum() - raw[c].isna().sum()
                    )
                }
            except Exception:
                # 原始 Excel 列名为别名（如"莫诺菲"/"潜力量"），按规范列名无法直接读取；
                # 无法做原始数值校验，跳过此列的 numeric_check（不影响其他校验项）
                numeric_check[c] = {"non_numeric_count": "n/a (column header normalized from alias)"}
        dup_count = int(self.df.duplicated(subset=["客户名称"]).sum()) if "客户名称" in self.df.columns else None
        return {
            "status": "passed" if not missing else "failed",
            "source_file": str(self.excel_path),
            "row_count": int(len(self.df)),
            "column_count": int(len(self.df.columns)),
            "required_columns_check": {"passed": not missing, "missing_columns": missing},
            "null_check": null_check,
            "numeric_check": numeric_check,
            "duplicate_check": {"duplicate_customer_name_count": dup_count},
            "products": list(self.product_mapping.keys()),
        }

    def cmd_list_values(self, args: argparse.Namespace) -> Dict[str, Any]:
        df, filters = self.apply_filters(self.df, args)
        field = self.resolve_field(args.field)
        if field not in df.columns:
            suggestion = self._suggest_column(field, list(df.columns))
            hint = f"，最相近字段：[{suggestion}]" if suggestion else ""
            available_text = [c for c in df.columns if df[c].dtype == object]
            raise ValueError(
                f"字段不存在：{field}{hint}。可用文本字段：{available_text}"
            )
        values = sorted([str(v) for v in df[field].dropna().unique() if str(v).strip() != ""])
        return {
            "meta": self.meta("list-values", len(self.df), len(df)),
            "query": {"command": "list-values", "field": field, "filters": filters},
            "values": values,
            "count": len(values),
        }

    def cmd_summary(self, args: argparse.Namespace) -> Dict[str, Any]:
        df, filters = self.apply_filters(self.df, args)
        return {
            "meta": self.meta("summary", len(self.df), len(df)),
            "query": {"command": "summary", "filters": filters},
            "summary": self.calc_summary(df),
        }

    def cmd_group(self, args: argparse.Namespace) -> Dict[str, Any]:
        df, filters = self.apply_filters(self.df, args)
        by = self.resolve_field(args.by)
        if by not in df.columns:
            # 尝试模糊匹配
            suggestion = self._suggest_column(by, list(df.columns))
            if suggestion:
                self._warn(f"分组字段 [{by}] 不存在，已自动回退为最相近字段 [{suggestion}]")
                by = suggestion
            else:
                available = [c for c in df.columns if df[c].dtype == object]
                raise ValueError(
                    f"分组字段不存在：{by}。可用文本字段：{available}"
                )
        rows = []
        for key, part in df.groupby(by, dropna=False):
            row = {by: normalize_value(key)}
            summary = self.calc_summary(part)
            row["hospital_count"] = summary["hospital_count"]
            row["total_potential"] = summary["total_potential"]
            for product, vals in summary["products"].items():
                row[f"{product}_total_flow"] = vals.get("total_flow")
                row[f"{product}_covered_hospital_count"] = vals.get("covered_hospital_count")
                row[f"{product}_coverage_rate"] = vals.get("coverage_rate")
                row[f"{product}_potential_conversion_rate"] = vals.get("potential_conversion_rate")
            rows.append(row)
        sort_by = args.sort_by or "total_potential"
        if rows and sort_by in rows[0]:
            rows.sort(key=lambda x: (x.get(sort_by) is None, x.get(sort_by)), reverse=args.desc)
        return {
            "meta": self.meta("group", len(self.df), len(df)),
            "query": {"command": "group", "group_by": by, "filters": filters},
            "rows": rows[: args.top] if args.top else rows,
        }

    def metric_series(self, df: pd.DataFrame, metric: str) -> pd.Series:
        metric = metric.strip()
        if metric in ["IDA患者数", "潜力量", "potential"]:
            if "IDA患者数" not in df.columns:
                self._warn("IDA患者数 列不存在，metric 返回全零序列")
                return pd.Series([0.0] * len(df), index=df.index, dtype=float)
            return to_number(df["IDA患者数"])
        if metric in ["医院数量", "hospital_count"]:
            return pd.Series([1] * len(df), index=df.index)
        for product in self.product_mapping:
            if metric in [f"{product}流向", f"{product}流向合计"]:
                try:
                    return to_number(df[self.product_flow_col(product)])
                except ValueError as e:
                    self._warn(f"metric {metric} 对应列不可用，返回全零序列：{e}")
                    return pd.Series([0.0] * len(df), index=df.index, dtype=float)
            if metric == f"{product}覆盖医院数":
                try:
                    return (to_number(df[self.product_flow_col(product)]) > 0).astype(int)
                except ValueError as e:
                    self._warn(f"metric {metric} 对应列不可用，返回全零序列：{e}")
                    return pd.Series([0] * len(df), index=df.index, dtype=int)
        # 未识别指标：列出全部可用值以辅助调用方修正
        available = (
            ["IDA患者数", "潜力量", "potential", "医院数量", "hospital_count"]
            + [f"{p}流向" for p in self.product_mapping]
            + [f"{p}覆盖医院数" for p in self.product_mapping]
        )
        raise ValueError(f"未知指标：{metric}。可用指标：{available}")

    def cmd_rank(self, args: argparse.Namespace) -> Dict[str, Any]:
        df, filters = self.apply_filters(self.df, args)
        by = self.resolve_field(args.by)
        metric = args.metric
        if by not in df.columns:
            suggestion = self._suggest_column(by, list(df.columns))
            if suggestion:
                self._warn(f"排名字段 [{by}] 不存在，已自动回退为最相近字段 [{suggestion}]")
                by = suggestion
            else:
                available = [c for c in df.columns if df[c].dtype == object]
                raise ValueError(f"排名字段不存在：{by}。可用文本字段：{available}")
        temp = df.copy()
        temp["__metric__"] = self.metric_series(temp, metric)
        grouped = temp.groupby(by, dropna=False)["__metric__"].sum().reset_index()
        grouped = grouped.sort_values("__metric__", ascending=not args.desc).head(args.top)
        rows = []
        for i, (_, r) in enumerate(grouped.iterrows(), start=1):
            row = {"rank": i, by: normalize_value(r[by]), metric: float(r["__metric__"])}
            # 如果按医院排名，补充核心维度
            if by == "客户名称":
                first = temp[temp[by] == r[by]].iloc[0]
                for c in ["大区", "区域", "省", "市", "区/县", "医院级别-大类", "客户性质", "类型名称", "IDA患者数"]:
                    if c in temp.columns:
                        row[c] = normalize_value(first[c])
                for product in self.product_mapping:
                    try:
                        row[f"{product}流向"] = float(first[self.product_flow_col(product)])
                    except (ValueError, KeyError):
                        # 产品列缺失时填 null，不因补充字段缺失而崩溃整个排名结果
                        row[f"{product}流向"] = None
            rows.append(row)
        return {
            "meta": self.meta("rank", len(self.df), len(df)),
            "query": {"command": "rank", "rank_by": by, "metric": metric, "filters": filters, "top": args.top},
            "rows": rows,
        }

    def cmd_product_compare(self, args: argparse.Namespace) -> Dict[str, Any]:
        df, filters = self.apply_filters(self.df, args)
        summary = self.calc_summary(df)
        products = list(self.product_mapping.keys())
        comparison = {}
        if len(products) >= 2:
            p1, p2 = products[0], products[1]
            try:
                c1 = self.product_flow_col(p1)
                f1: pd.Series = to_number(df[c1])
            except (ValueError, KeyError) as e:
                self._warn(f"product-compare: {p1} 列不可用，对比结果将含 null：{e}")
                f1 = pd.Series([0.0] * len(df), index=df.index, dtype=float)
                c1 = None
            try:
                c2 = self.product_flow_col(p2)
                f2: pd.Series = to_number(df[c2])
            except (ValueError, KeyError) as e:
                self._warn(f"product-compare: {p2} 列不可用，对比结果将含 null：{e}")
                f2 = pd.Series([0.0] * len(df), index=df.index, dtype=float)
                c2 = None
            total1, total2 = float(f1.sum()), float(f2.sum())
            comparison = {
                "product_a": p1,
                "product_b": p2,
                "product_a_column_found": c1 is not None,
                "product_b_column_found": c2 is not None,
                "flow_gap_a_minus_b": total1 - total2,
                "flow_ratio_a_divide_b": None if total2 == 0 else total1 / total2,
                "both_covered_hospital_count": int(((f1 > 0) & (f2 > 0)).sum()),
                f"only_{p1}_covered_count": int(((f1 > 0) & (f2 == 0)).sum()),
                f"only_{p2}_covered_count": int(((f1 == 0) & (f2 > 0)).sum()),
                "both_uncovered_hospital_count": int(((f1 == 0) & (f2 == 0)).sum()),
                f"{p1}_returned_count": int((f1 < 0).sum()),
                f"{p2}_returned_count": int((f2 < 0).sum()),
                "both_returned_hospital_count": int(((f1 < 0) & (f2 < 0)).sum()),
            }
        return {
            "meta": self.meta("product-compare", len(self.df), len(df)),
            "query": {"command": "product-compare", "filters": filters},
            "summary": summary,
            "comparison": comparison,
        }

    def cmd_detail(self, args: argparse.Namespace) -> Dict[str, Any]:
        df, filters = self.apply_filters(self.df, args)
        if args.sort_by:
            sort_by = self.resolve_field(args.sort_by)
            if sort_by in df.columns:
                df = df.sort_values(sort_by, ascending=not args.desc)
            elif sort_by in [f"{p}流向" for p in self.product_mapping]:
                df = df.sort_values(sort_by, ascending=not args.desc)
            else:
                # 容错：排序字段不存在时警告并跳过，不崩溃
                suggestion = self._suggest_column(sort_by, list(df.columns))
                hint = f"，最相近字段：[{suggestion}]" if suggestion else ""
                self._warn(f"排序字段 [{sort_by}] 不存在{hint}，已跳过排序")
        if args.top:
            df = df.head(args.top)
        rows = self.format_detail_rows(df)
        return {
            "meta": self.meta("detail", len(self.df), len(df)),
            "query": {"command": "detail", "filters": filters, "top": args.top},
            "rows": rows,
        }

    def format_detail_rows(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        base_cols = ["大区", "区域", "客户名称", "客户性质", "类型名称", "客户级别", "医院级别-大类", "省", "市", "区/县", "IDA患者数"]
        rows = []
        for _, r in df.iterrows():
            item = {c: normalize_value(r[c]) for c in base_cols if c in df.columns}
            item["products"] = {}
            for product, conf in self.product_mapping.items():
                col = conf["flow_column"]
                if col in df.columns:
                    item["products"][product] = {
                        "flow": float(r[col]),
                        "spec": conf.get("spec"),
                        "period": conf.get("period"),
                    }
            rows.append(item)
        return rows

    def cmd_hospital(self, args: argparse.Namespace) -> Dict[str, Any]:
        setattr(args, "客户名称", args.name)
        setattr(args, "fuzzy", args.fuzzy)
        df, filters = self.apply_filters(self.df, args)
        return {
            "meta": self.meta("hospital", len(self.df), len(df)),
            "query": {"command": "hospital", "name": args.name, "fuzzy": args.fuzzy},
            "matches": self.format_detail_rows(df),
        }

    def cmd_opportunity(self, args: argparse.Namespace) -> Dict[str, Any]:
        df, filters = self.apply_filters(self.df, args)
        typ = args.type
        reason = ""
        if typ in ["uncovered-high-potential", "high-potential-zero-flow"]:
            if not args.产品:
                raise ValueError("该机会类型必须指定 --产品")
            col = self.product_flow_col(args.产品)
            df = df[to_number(df[col]) == 0]
            reason = f"高IDA患者数且{args.产品}严格未覆盖（flow=0）"
        elif typ == "returned-followup":
            if not args.产品:
                raise ValueError("returned-followup 必须指定 --产品")
            col = self.product_flow_col(args.产品)
            df = df[to_number(df[col]) < 0]
            reason = f"{args.产品}已覆盖但产生退货异常，需追溯销售跟进/学术资源/有效期管理"
        elif typ == "high-potential-low-flow":
            if not args.产品:
                raise ValueError("该机会类型必须指定 --产品")
            col = self.product_flow_col(args.产品)
            threshold = args.max_flow if args.max_flow is not None else 10
            df = df[to_number(df[col]) <= threshold]
            reason = f"高IDA患者数且{args.产品}流向较低"
        elif typ == "product-gap":
            if not args.covered_product or not args.uncovered_product:
                raise ValueError("product-gap 必须指定 --covered-product 和 --uncovered-product")
            c1 = self.product_flow_col(args.covered_product)
            c2 = self.product_flow_col(args.uncovered_product)
            df = df[(to_number(df[c1]) > 0) & (to_number(df[c2]) == 0)]
            reason = f"{args.covered_product}已覆盖但{args.uncovered_product}严格未覆盖"
        else:
            raise ValueError(f"未知机会类型：{typ}")

        if args.min_potential is not None and "IDA患者数" in df.columns:
            df = df[df["IDA患者数"] >= args.min_potential]
        if "IDA患者数" in df.columns:
            df = df.sort_values("IDA患者数", ascending=False)
        else:
            self._warn("IDA患者数 列不存在，opportunity 结果未按患者数排序")
        if args.top:
            df = df.head(args.top)
        rows = self.format_detail_rows(df)
        for i, row in enumerate(rows, start=1):
            row["rank"] = i
            row["reason"] = reason
        return {
            "meta": self.meta("opportunity", len(self.df), len(df)),
            "query": {"command": "opportunity", "type": typ, "filters": filters, "top": args.top},
            "summary": {
                "candidate_hospital_count": len(rows),
                "candidate_total_potential": float(df["IDA患者数"].sum()) if "IDA患者数" in df.columns else None,
            },
            "rows": rows,
        }


def add_common_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--大区")
    parser.add_argument("--区域")
    parser.add_argument("--省")
    parser.add_argument("--市")
    parser.add_argument("--区县")
    parser.add_argument("--客户名称")
    parser.add_argument("--客户性质")
    parser.add_argument("--类型名称")
    parser.add_argument("--客户级别")
    parser.add_argument("--医院级别大类")
    parser.add_argument("--min-potential", type=float)
    parser.add_argument("--max-potential", type=float)
    parser.add_argument("--产品")
    parser.add_argument("--flow-status", choices=["covered", "uncovered", "returned", "not-covered"])
    parser.add_argument("--min-flow", type=float)
    parser.add_argument("--max-flow", type=float)
    parser.add_argument("--fuzzy", action="store_true", help="模糊匹配文本筛选，尤其适合医院名称")


def add_common_io_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=["json", "markdown", "csv"], default=argparse.SUPPRESS, help="输出格式")
    parser.add_argument("--output", default=argparse.SUPPRESS, help="输出到文件")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="医院基础数据 CLI 查询工具")
    parser.add_argument("--excel", default=str(DEFAULT_EXCEL), help="Excel 文件路径，默认 references/hospital_base.xlsx")
    parser.add_argument("--sheet", default=None, help="Excel 工作表名称，不填则读取第一个工作表")
    parser.add_argument("--format", default="json", choices=["json", "markdown", "csv"], help="输出格式")
    parser.add_argument("--output", default=None, help="输出到文件")
    parser.add_argument("--query-id", default=None, help="本次查询 ID，用于审计追踪；不填则自动生成")
    parser.add_argument("--query-output-dir", default=None, help="保存带追踪信息的 JSON 查询结果目录")

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="校验数据源")
    add_common_io_args(p)

    p = sub.add_parser("list-values", help="列出某字段的可选值")
    add_common_io_args(p)
    add_common_filters(p)
    p.add_argument("--field", required=True)

    p = sub.add_parser("summary", help="整体汇总")
    add_common_io_args(p)
    add_common_filters(p)

    p = sub.add_parser("group", help="分组汇总")
    add_common_io_args(p)
    add_common_filters(p)
    p.add_argument("--by", required=True)
    p.add_argument("--sort-by", default=None)
    p.add_argument("--desc", action="store_true")
    p.add_argument("--top", type=int)

    p = sub.add_parser("rank", help="排名查询")
    add_common_io_args(p)
    add_common_filters(p)
    p.add_argument("--by", required=True)
    p.add_argument("--metric", required=True)
    p.add_argument("--top", type=int, default=20)
    p.add_argument("--desc", action="store_true", default=True)

    p = sub.add_parser("product-compare", help="产品对比")
    add_common_io_args(p)
    add_common_filters(p)

    p = sub.add_parser("detail", help="明细查询")
    add_common_io_args(p)
    add_common_filters(p)
    p.add_argument("--sort-by")
    p.add_argument("--desc", action="store_true")
    p.add_argument("--top", type=int)

    p = sub.add_parser("hospital", help="单医院查询")
    add_common_io_args(p)
    add_common_filters(p)
    p.add_argument("--name", required=True)

    p = sub.add_parser("opportunity", help="机会点分析")
    add_common_io_args(p)
    add_common_filters(p)
    p.add_argument("--type", required=True, choices=["high-potential-low-flow", "high-potential-zero-flow", "uncovered-high-potential", "product-gap", "returned-followup"])
    p.add_argument("--covered-product")
    p.add_argument("--uncovered-product")
    p.add_argument("--top", type=int, default=20)

    return parser


def build_query_id(args: argparse.Namespace) -> str:
    if args.query_id:
        return args.query_id
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    command = getattr(args, "command", "query")
    province = getattr(args, "省", None) or "ALL"
    return f"HDQ-{province}-{command}-{stamp}"


def _detect_workspace_root(path: Path) -> Optional[Path]:
    """Locate the nearest ancestor that looks like a province workspace root.

    A workspace is identified by containing 00_input/ and (data_queries/ or 02_task_outputs/).
    """
    for ancestor in [path, *path.parents]:
        if (ancestor / "00_input").is_dir() and (
            (ancestor / "data_queries").is_dir() or (ancestor / "02_task_outputs").is_dir()
        ):
            return ancestor
    return None


def _to_workspace_relative(path: Path) -> str:
    """If the path lives inside a workspace, return the workspace-relative form.

    Otherwise return the absolute resolved path. This keeps audit traces portable
    across machines/checkouts without losing reachability for ad-hoc runs.
    """
    abs_path = path.resolve()
    workspace = _detect_workspace_root(abs_path)
    if workspace is None:
        return str(abs_path)
    try:
        return str(abs_path.relative_to(workspace.resolve()))
    except ValueError:
        return str(abs_path)


def attach_query_trace(result: Dict[str, Any], args: argparse.Namespace, result_path: Optional[Path] = None) -> Dict[str, Any]:
    excel_abs = Path(args.excel).resolve()
    trace = {
        "query_id": build_query_id(args),
        "command": getattr(args, "command", ""),
        "command_line": " ".join(sys.argv),
        "source_file": _to_workspace_relative(excel_abs),
        "source_file_abs": str(excel_abs),
        "sheet": args.sheet,
        "result_path": _to_workspace_relative(result_path) if result_path else "",
        "result_path_abs": str(result_path.resolve()) if result_path else "",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    result["internal_query_trace"] = trace
    return result


def save_query_result(result: Dict[str, Any], query_output_dir: Optional[str], args: argparse.Namespace) -> Optional[Path]:
    if not query_output_dir:
        return None
    out_dir = Path(query_output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    query_id = build_query_id(args)
    out_path = out_dir / f"{query_id}.json"
    attach_query_trace(result, args, out_path)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    return out_path


def output_result(result: Dict[str, Any], fmt: str, output: Optional[str]) -> None:
    if fmt == "json":
        text = json.dumps(result, ensure_ascii=False, indent=2, default=json_default)
    elif fmt == "markdown":
        text = "```json\n" + json.dumps(result, ensure_ascii=False, indent=2, default=json_default) + "\n```"
    elif fmt == "csv":
        rows = result.get("rows") or result.get("matches") or []
        if not rows:
            rows = [result.get("summary", result)]
        df = pd.json_normalize(rows)
        text = df.to_csv(index=False)
    else:
        raise ValueError(f"未知输出格式：{fmt}")

    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args(normalize_global_args(sys.argv[1:]))
    try:
        cli = DataCLI(Path(args.excel), args.sheet)
        if args.command == "validate":
            result = cli.cmd_validate()
        elif args.command == "list-values":
            result = cli.cmd_list_values(args)
        elif args.command == "summary":
            result = cli.cmd_summary(args)
        elif args.command == "group":
            result = cli.cmd_group(args)
        elif args.command == "rank":
            result = cli.cmd_rank(args)
        elif args.command == "product-compare":
            result = cli.cmd_product_compare(args)
        elif args.command == "detail":
            result = cli.cmd_detail(args)
        elif args.command == "hospital":
            result = cli.cmd_hospital(args)
        elif args.command == "opportunity":
            result = cli.cmd_opportunity(args)
        else:
            raise ValueError(f"未知命令：{args.command}")
        query_result_path = save_query_result(result, args.query_output_dir, args)
        if "internal_query_trace" not in result:
            attach_query_trace(result, args, query_result_path)
        output_result(result, args.format, args.output)
    except Exception as e:
        err = {"status": "error", "message": str(e)}
        print(json.dumps(err, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
