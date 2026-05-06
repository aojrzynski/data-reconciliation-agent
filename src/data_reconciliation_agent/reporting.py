"""Write human-readable deterministic reconciliation markdown report."""

from __future__ import annotations

from pathlib import Path


def write_report(output_dir: Path, report_data: dict) -> str:
    report_path = output_dir / "reconciliation_report.md"
    lines = [
        "# Reconciliation Report",
        "",
        "This report contains deterministic reconciliation output.",
        "",
        "## Input summary",
        f"- Source: `{report_data['source_path']}`",
        f"- Target: `{report_data['target_path']}`",
        f"- Key mode: `{report_data['key_mode']}`",
        f"- Source key: `{report_data['source_key']}`",
        f"- Target key: `{report_data['target_key']}`",
        f"- Mapping file: `{report_data['mapping_config_path']}`" if report_data.get("mapping_config_path") else "- Mapping file: (none)",
        f"- Source rows: {report_data['source_row_count']}",
        f"- Target rows: {report_data['target_row_count']}",
        "",
    ]

    if report_data.get("mapping_config"):
        mapping = report_data["mapping_config"]
        lines.extend([
            "## Mapping config summary",
            f"- Entity: `{mapping['entity']}`",
            f"- Source key: `{mapping['source_key']}`",
            f"- Target key: `{mapping['target_key']}`",
            f"- Number of mapped fields: {mapping['mapped_field_count']}",
            f"- Planned comparator types: {', '.join(mapping['planned_comparators']) or '(none)'}",
            "",
        ])

    lines.extend([
        "## Key summary",
        f"- Key exists in source: {report_data['key_checks']['key_exists_in_source']}",
        f"- Key exists in target: {report_data['key_checks']['key_exists_in_target']}",
        f"- Null key rows in source: {report_data['key_checks']['null_key_count_source']}",
        f"- Null key rows in target: {report_data['key_checks']['null_key_count_target']}",
        f"- Duplicate key rows in source: {report_data['key_checks']['duplicate_key_row_count_source']}",
        f"- Duplicate key rows in target: {report_data['key_checks']['duplicate_key_row_count_target']}",
        "",
        "## Row/record reconciliation summary",
        f"- Matched keys: {report_data['record_comparison']['matched_key_count']}",
        f"- Missing from target: {report_data['record_comparison']['missing_in_target_count']}",
        f"- Unexpected in target: {report_data['record_comparison']['unexpected_in_target_count']}",
        "",
        "## Value comparison summary",
        "Value comparison only runs for records matched by key. Missing and unexpected records are handled separately.",
        f"- Ran: {report_data['value_comparison']['enabled']}",
        f"- Skipped reason: {report_data['value_comparison']['skipped_reason']}",
        f"- Matched records compared: {report_data['value_comparison']['matched_records_compared']}",
        f"- Mapped fields compared: {report_data['value_comparison']['fields_compared']}",
        f"- Total field comparisons: {report_data['value_comparison']['total_field_comparisons']}",
        f"- Total value mismatches: {report_data['value_comparison']['mismatched_value_count']}",
        "- Mismatches by field:",
        "",
        "## Exception files written",
    ])
    lines.extend(
        [f"  - {k}: {v}" for k, v in report_data["value_comparison"]["mismatched_field_counts"].items()]
        or ["  - (none)"]
    )
    lines.extend([
        f"- value_mismatches.csv written: {'value_mismatches.csv' in report_data['output_files']['exceptions_written']}",
        "",
    ])
    lines.extend([f"- {n}" for n in report_data["output_files"]["exceptions_written"]] or ["- (none)"])
    lines.extend(["", "## Exception files not created because there were no relevant rows"])
    lines.extend([f"- {n}" for n in report_data["output_files"]["exceptions_skipped_empty"]] or ["- (none)"])
    lines.extend(["", "## Skipped checks"])
    lines.extend([f"- {n}" for n in report_data["checks_skipped"]] or ["- (none)"])
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {warning}" for warning in report_data["warnings"]] or ["- (none)"])
    lines.extend(["", "## Blocking errors"])
    lines.extend([f"- {error}" for error in report_data["blocking_errors"]] or ["- (none)"])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(report_path)
