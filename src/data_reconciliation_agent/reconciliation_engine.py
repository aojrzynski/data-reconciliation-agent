"""Deterministic reconciliation engine for Milestone 2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .exception_writer import write_exception_csv
from .intake import load_dataset
from .reconciliation_checks import duplicate_keys, key_exists, missing_keys, null_keys, unexpected_keys
from .reporting import write_report
from .schema_summary import build_schema_summary
from .trace_writer import write_trace


@dataclass(frozen=True)
class ReconciliationResult:
    source_row_count: int
    target_row_count: int
    matched_key_count: int
    missing_in_target_count: int
    unexpected_in_target_count: int
    report_path: str
    trace_path: str
    warnings: list[str]
    skipped_steps: list[str]


def run_deterministic_reconciliation(source_path: str, target_path: str, key: str, output_dir: str) -> ReconciliationResult:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    source = load_dataset(source_path)
    target = load_dataset(target_path)
    schema = build_schema_summary(source.dataframe, target.dataframe)

    key_in_source = key_exists(source.dataframe, key)
    key_in_target = key_exists(target.dataframe, key)
    warnings: list[str] = []
    skipped_steps: list[str] = []

    null_source = duplicate_source = missing_df = source.dataframe.iloc[0:0].copy()
    null_target = duplicate_target = unexpected_df = target.dataframe.iloc[0:0].copy()
    matched_key_count = 0

    if key_in_source:
        null_source = null_keys(source.dataframe, key)
        duplicate_source = duplicate_keys(source.dataframe, key)
    else:
        warnings.append(f"Key column '{key}' not found in source dataset.")
    if key_in_target:
        null_target = null_keys(target.dataframe, key)
        duplicate_target = duplicate_keys(target.dataframe, key)
    else:
        warnings.append(f"Key column '{key}' not found in target dataset.")

    if key_in_source and key_in_target:
        missing_df = missing_keys(source.dataframe, target.dataframe, key)
        unexpected_df = unexpected_keys(source.dataframe, target.dataframe, key)
        source_keys = set(source.dataframe[key].astype("string").str.strip().dropna())
        target_keys = set(target.dataframe[key].astype("string").str.strip().dropna())
        source_keys.discard("")
        target_keys.discard("")
        matched_key_count = len(source_keys & target_keys)
    else:
        skipped_steps.append("Record-level key comparison skipped because key column is missing in source or target.")

    exceptions_written: list[str] = []
    exceptions_skipped: list[str] = []
    for filename, frame in [
        ("missing_in_target.csv", missing_df),
        ("unexpected_in_target.csv", unexpected_df),
        ("duplicate_keys_source.csv", duplicate_source),
        ("duplicate_keys_target.csv", duplicate_target),
        ("null_keys_source.csv", null_source),
        ("null_keys_target.csv", null_target),
    ]:
        if write_exception_csv(out, filename, frame):
            exceptions_written.append(filename)
        else:
            exceptions_skipped.append(filename)
            skipped_steps.append(f"Skipped writing {filename} because there were no relevant rows.")

    trace_filename = "reconciliation_trace.json"
    report_filename = "reconciliation_report.md"
    trace_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "deterministic",
        "source_path": source.path,
        "target_path": target.path,
        "key": key,
        "source_row_count": source.row_count,
        "target_row_count": target.row_count,
        "source_columns": schema.source_columns,
        "target_columns": schema.target_columns,
        "source_only_columns": schema.source_only_columns,
        "target_only_columns": schema.target_only_columns,
        "common_columns": schema.common_columns,
        "key_checks": {
            "key_exists_in_source": key_in_source,
            "key_exists_in_target": key_in_target,
            "null_key_count_source": len(null_source),
            "null_key_count_target": len(null_target),
            "duplicate_key_row_count_source": len(duplicate_source),
            "duplicate_key_row_count_target": len(duplicate_target),
        },
        "record_comparison": {
            "matched_key_count": matched_key_count,
            "missing_in_target_count": len(missing_df),
            "unexpected_in_target_count": len(unexpected_df),
        },
        "output_files": {
            "trace": trace_filename,
            "report": report_filename,
            "exceptions_written": exceptions_written,
            "exceptions_skipped": exceptions_skipped,
        },
        "warnings": warnings,
        "skipped_steps": skipped_steps,
    }

    trace_path = write_trace(out, trace_data)
    report_path = write_report(out, trace_data)

    return ReconciliationResult(
        source_row_count=source.row_count,
        target_row_count=target.row_count,
        matched_key_count=matched_key_count,
        missing_in_target_count=len(missing_df),
        unexpected_in_target_count=len(unexpected_df),
        report_path=report_path,
        trace_path=trace_path,
        warnings=warnings,
        skipped_steps=skipped_steps,
    )
