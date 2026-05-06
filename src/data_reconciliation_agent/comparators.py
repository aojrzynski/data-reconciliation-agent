"""Deterministic field comparators for mapped value comparison."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ComparisonOutcome:
    matched: bool
    source_normalized: str | float | date | datetime | None
    target_normalized: str | float | date | datetime | None
    reason: str


def _is_nullish(value: Any) -> bool:
    if pd.isna(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def compare_values(
    source_value: Any,
    target_value: Any,
    comparator: str,
    normalize: dict | None = None,
    tolerance: float | None = None,
) -> ComparisonOutcome:
    if _is_nullish(source_value) and _is_nullish(target_value):
        return ComparisonOutcome(True, None, None, "both_null")
    if _is_nullish(source_value) != _is_nullish(target_value):
        return ComparisonOutcome(False, None if _is_nullish(source_value) else source_value, None if _is_nullish(target_value) else target_value, "one_null")

    if comparator == "string":
        return compare_string(source_value, target_value, normalize=normalize)
    if comparator == "number":
        return compare_number(source_value, target_value, tolerance=tolerance)
    if comparator == "date":
        return compare_date(source_value, target_value)
    if comparator == "datetime":
        return compare_datetime(source_value, target_value)

    raise ValueError(f"Unsupported comparator: {comparator}")


def compare_string(source_value: Any, target_value: Any, normalize: dict | None = None) -> ComparisonOutcome:
    normalize = normalize or {}
    trim = normalize.get("trim", True)
    case_sensitive = normalize.get("case_sensitive", True)

    source = str(source_value)
    target = str(target_value)
    if trim:
        source = source.strip()
        target = target.strip()
    if not case_sensitive:
        source = source.lower()
        target = target.lower()

    return ComparisonOutcome(source == target, source, target, "equal" if source == target else "value_mismatch")


def compare_number(source_value: Any, target_value: Any, tolerance: float | None = None) -> ComparisonOutcome:
    source_num = pd.to_numeric(source_value, errors="coerce")
    target_num = pd.to_numeric(target_value, errors="coerce")

    if pd.isna(source_num) or pd.isna(target_num):
        return ComparisonOutcome(False, None if pd.isna(source_num) else float(source_num), None if pd.isna(target_num) else float(target_num), "number_parse_error")

    source_float = float(source_num)
    target_float = float(target_num)
    if tolerance is None:
        matched = source_float == target_float
    else:
        matched = abs(source_float - target_float) <= float(tolerance)
    return ComparisonOutcome(matched, source_float, target_float, "equal" if matched else "value_mismatch")


def compare_date(source_value: Any, target_value: Any) -> ComparisonOutcome:
    source_dt = pd.to_datetime(source_value, errors="coerce", utc=True)
    target_dt = pd.to_datetime(target_value, errors="coerce", utc=True)
    if pd.isna(source_dt) or pd.isna(target_dt):
        return ComparisonOutcome(False, None if pd.isna(source_dt) else str(source_dt.date()), None if pd.isna(target_dt) else str(target_dt.date()), "date_parse_error")

    source_date = source_dt.date().isoformat()
    target_date = target_dt.date().isoformat()
    return ComparisonOutcome(source_date == target_date, source_date, target_date, "equal" if source_date == target_date else "value_mismatch")


def compare_datetime(source_value: Any, target_value: Any) -> ComparisonOutcome:
    source_dt = pd.to_datetime(source_value, errors="coerce", utc=True)
    target_dt = pd.to_datetime(target_value, errors="coerce", utc=True)
    if pd.isna(source_dt) or pd.isna(target_dt):
        return ComparisonOutcome(False, None if pd.isna(source_dt) else str(source_dt), None if pd.isna(target_dt) else str(target_dt), "datetime_parse_error")

    source_norm = source_dt.to_pydatetime().astimezone(timezone.utc).replace(tzinfo=timezone.utc).isoformat()
    target_norm = target_dt.to_pydatetime().astimezone(timezone.utc).replace(tzinfo=timezone.utc).isoformat()
    return ComparisonOutcome(source_norm == target_norm, source_norm, target_norm, "equal" if source_norm == target_norm else "value_mismatch")
