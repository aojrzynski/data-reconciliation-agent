"""Deterministic reconciliation engine for Milestone 3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .exception_writer import write_exception_csv
from .intake import load_dataset
from .mapping import load_mapping_config, mapping_config_to_trace_dict, validate_mapping_config
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
    blocking_errors: list[str]
    skipped_steps: list[str]
    key_mode: str
    source_key: str
    target_key: str


def run_deterministic_reconciliation(
    source_path: str,
    target_path: str,
    output_dir: str,
    key: str | None = None,
    mapping_path: str | None = None,
) -> ReconciliationResult:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    source = load_dataset(source_path)
    target = load_dataset(target_path)
    schema = build_schema_summary(source.dataframe, target.dataframe)

    warnings: list[str] = []
    blocking_errors: list[str] = []
    skipped_steps: list[str] = []

    mapping_summary: dict | None = None
    validation_errors: list[str] = []
    if mapping_path:
        if key:
            warnings.append(
                "--mapping was provided, so source_key/target_key from mapping config are used and --key is ignored."
            )
        mapping_config = load_mapping_config(mapping_path)
        source_key = mapping_config.source_key
        target_key = mapping_config.target_key
        key_mode = "mapping_config"
        mapping_summary = mapping_config_to_trace_dict(mapping_config)
        validation_errors = validate_mapping_config(mapping_config, schema.source_columns, schema.target_columns)
    else:
        if not key:
            raise ValueError("deterministic mode requires either --key or --mapping")
        source_key = key
        target_key = key
        key_mode = "explicit_same_name_key"

    key_in_source = key_exists(source.dataframe, source_key)
    key_in_target = key_exists(target.dataframe, target_key)

    null_source = duplicate_source = missing_df = source.dataframe.iloc[0:0].copy()
    null_target = duplicate_target = unexpected_df = target.dataframe.iloc[0:0].copy()
    matched_key_count = 0

    if key_in_source:
        null_source = null_keys(source.dataframe, source_key)
        duplicate_source = duplicate_keys(source.dataframe, source_key)
    else:
        message = f"Key column '{source_key}' not found in source dataset."
        warnings.append(message)
        blocking_errors.append(message)
    if key_in_target:
        null_target = null_keys(target.dataframe, target_key)
        duplicate_target = duplicate_keys(target.dataframe, target_key)
    else:
        message = f"Key column '{target_key}' not found in target dataset."
        warnings.append(message)
        blocking_errors.append(message)

    if validation_errors:
        blocking_errors.extend(validation_errors)
        warnings.extend(validation_errors)

    if key_in_source and key_in_target and not validation_errors:
        missing_df = missing_keys(source.dataframe, target.dataframe, source_key, target_key)
        unexpected_df = unexpected_keys(source.dataframe, target.dataframe, source_key, target_key)
        source_keys = set(source.dataframe[source_key].astype("string").str.strip().dropna())
        target_keys = set(target.dataframe[target_key].astype("string").str.strip().dropna())
        source_keys.discard("")
        target_keys.discard("")
        matched_key_count = len(source_keys & target_keys)
    else:
        skipped_steps.append("Record-level key comparison skipped because key columns are invalid or failed mapping validation.")

    exceptions_written: list[str] = []
    exceptions_skipped_empty: list[str] = []
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
            exceptions_skipped_empty.append(filename)

    trace_filename = "reconciliation_trace.json"
    report_filename = "reconciliation_report.md"
    trace_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "deterministic",
        "source_path": source.path,
        "target_path": target.path,
        "key": key,
        "key_mode": key_mode,
        "source_key": source_key,
        "target_key": target_key,
        "mapping_config_path": mapping_path,
        "mapping_config": mapping_summary,
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
            "exceptions_skipped_empty": exceptions_skipped_empty,
        },
        "checks_skipped": skipped_steps,
        "validation_errors": validation_errors,
        "warnings": warnings,
        "blocking_errors": blocking_errors,
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
        blocking_errors=blocking_errors,
        skipped_steps=skipped_steps,
        key_mode=key_mode,
        source_key=source_key,
        target_key=target_key,
    )
