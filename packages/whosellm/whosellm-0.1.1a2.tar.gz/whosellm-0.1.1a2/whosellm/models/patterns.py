# filename: patterns.py
# @Time    : 2025/11/7 17:06
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型命名模式定义 / Model naming pattern definitions

使用 parse 库进行模式匹配，提供清晰、高性能的模型名称解析
Using parse library for pattern matching, providing clear and high-performance model name parsing
"""

from datetime import date, datetime
from typing import Any

import parse  # type: ignore[import-untyped]


def _convert_variant(text: str) -> str:
    if not text:
        msg = "variant must be non-empty"
        raise ValueError(msg)

    first = text[0]
    if not first.isalpha():
        msg = "variant must start with a letter"
        raise ValueError(msg)

    for ch in text:
        if ch.isalnum() or ch == "-":
            continue
        msg = "variant may only contain letters, digits, or '-'"
        raise ValueError(msg)

    return text


DEFAULT_EXTRA_TYPES: dict[str, Any] = {"variant": _convert_variant}


def _merge_extra_types(extra_types: dict[str, Any] | None) -> dict[str, Any]:
    if not extra_types:
        return dict(DEFAULT_EXTRA_TYPES)

    merged = dict(DEFAULT_EXTRA_TYPES)
    merged.update(extra_types)
    return merged


def parse_pattern(
    pattern: str,
    text: str,
    *,
    extra_types: dict[str, Any] | None = None,
) -> parse.Result | None:
    try:
        return parse.parse(pattern, text, extra_types=_merge_extra_types(extra_types))
    except ValueError:
        return None


def parse_date_from_match(matched: dict[str, Any]) -> date | None:
    if all(k in matched for k in ["year", "month", "day"]):
        try:
            return date(matched["year"], matched["month"], matched["day"])
        except (ValueError, TypeError):
            pass

    if "mmdd" in matched:
        try:
            mmdd_str = str(matched["mmdd"]).zfill(4)
            month = int(mmdd_str[:2])
            day = int(mmdd_str[2:])
            # 默认当前年份
            year = datetime.now().year
            return date(year=year, month=month, day=day)
        except (ValueError, TypeError):
            pass

    return None


def normalize_variant(variant: str | None) -> str:
    if not variant:
        return "base"

    variant = variant.lower().strip()

    suffixes_to_remove = ["custom", "test", "latest", "new", "experimental", "v1", "v2", "v3"]

    parts = variant.split("-")

    filtered_parts = [p for p in parts if p not in suffixes_to_remove]

    if filtered_parts:
        return "-".join(filtered_parts)

    return "base"
