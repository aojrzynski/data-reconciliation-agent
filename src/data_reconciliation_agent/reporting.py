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
        "This report compares record presence using the configured key. It does not yet compare mapped field values.",
        "",
        "## Input summary",
        f"- Source: `{report_data['source_path']}`",
        f"- Target: `{report_data['target_path']}`",
        f"- Key: `{report_data['key']}`",
        f"- Source rows: {report_data['source_row_count']}",
        f"- Target rows: {report_data['target_row_count']}",
        "",
        "## Key summary",
        f"- Key exists in source: {report_data['key_checks']['key_exists_in_source']}",
        f"- Key exists in target: {report_data['key_checks']['key_exists_in_target']}",
        f"- Null keys in source: {report_data['key_checks']['null_key_count_source']}",
        f"- Null keys in target: {report_data['key_checks']['null_key_count_target']}",
        f"- Duplicate key rows in source: {report_data['key_checks']['duplicate_key_row_count_source']}",
        f"- Duplicate key rows in target: {report_data['key_checks']['duplicate_key_row_count_target']}",
        "",
        "## Row/record reconciliation summary",
        f"- Matched keys: {report_data['record_comparison']['matched_key_count']}",
        f"- Missing from target: {report_data['record_comparison']['missing_in_target_count']}",
        f"- Unexpected in target: {report_data['record_comparison']['unexpected_in_target_count']}",
        "",
        "## Column summary",
        f"- Source-only columns: {', '.join(report_data['source_only_columns']) or '(none)'}",
        f"- Target-only columns: {', '.join(report_data['target_only_columns']) or '(none)'}",
        f"- Common columns: {', '.join(report_data['common_columns']) or '(none)'}",
        "",
        "## Exception files",
        "### Written",
    ]
    written = report_data["output_files"]["exceptions_written"]
    skipped = report_data["output_files"]["exceptions_skipped"]
    lines.extend([f"- {n}" for n in written] or ["- (none)"])
    lines.extend(["", "### Skipped (no relevant rows)"])
    lines.extend([f"- {n}" for n in skipped] or ["- (none)"])

    lines.extend(["", "## Warnings"])
    lines.extend([f"- {warning}" for warning in report_data["warnings"]] or ["- (none)"])

    lines.extend(["", "## Skipped checks"])
    lines.extend([f"- {step}" for step in report_data["skipped_steps"]] or ["- (none)"])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(report_path)
