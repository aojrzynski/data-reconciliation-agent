"""Deterministic source/target schema summary helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SchemaSummary:
    source_row_count: int
    target_row_count: int
    source_column_count: int
    target_column_count: int
    source_columns: list[str]
    target_columns: list[str]
    source_only_columns: list[str]
    target_only_columns: list[str]
    common_columns: list[str]


def build_schema_summary(source_df: pd.DataFrame, target_df: pd.DataFrame) -> SchemaSummary:
    source_columns = [str(c) for c in source_df.columns.tolist()]
    target_columns = [str(c) for c in target_df.columns.tolist()]
    source_set = set(source_columns)
    target_set = set(target_columns)

    return SchemaSummary(
        source_row_count=len(source_df),
        target_row_count=len(target_df),
        source_column_count=len(source_columns),
        target_column_count=len(target_columns),
        source_columns=source_columns,
        target_columns=target_columns,
        source_only_columns=sorted(source_set - target_set),
        target_only_columns=sorted(target_set - source_set),
        common_columns=sorted(source_set & target_set),
    )
