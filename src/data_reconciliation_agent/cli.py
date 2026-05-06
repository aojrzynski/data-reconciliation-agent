"""CLI entrypoint for the Data Reconciliation Agent."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="data-reconciliation-agent", description="CLI for deterministic data reconciliation.")
    parser.add_argument("--source", help="Path to source dataset file (CSV or XLSX).")
    parser.add_argument("--target", help="Path to target dataset file (CSV or XLSX).")
    parser.add_argument("--key", help="Explicit same-name key column for deterministic mode.")
    parser.add_argument("--mapping", help="Optional YAML mapping file path.")
    parser.add_argument("--mode", choices=["deterministic", "agent"], default="deterministic")
    parser.add_argument("--output-dir", default="outputs", help="Output directory for artifacts.")
    parser.add_argument("--llm-summary", action="store_true", help="Optional future LLM summary flag.")
    parser.add_argument("--confirm-assumptions", action="store_true", help="Ask for y/yes before running inferred assumptions.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.source or not args.target:
        parser.error(f"{args.mode} mode requires --source and --target")

    if args.mode == "agent":
        from .agent_runner import run_agent_reconciliation

        if args.llm_summary:
            print("Warning: --llm-summary is planned for a later milestone and is ignored.")
        try:
            result = run_agent_reconciliation(
                source_path=args.source,
                target_path=args.target,
                output_dir=args.output_dir,
                key=args.key,
                mapping_path=args.mapping,
                confirm_assumptions=args.confirm_assumptions,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1

        print(f"Agent mode {result.status}.")
        print(f"Plan status: {result.plan.status}")
        print(f"Key mode: {result.plan.key_mode}")
        print(f"Source key: {result.plan.source_key}")
        print(f"Target key: {result.plan.target_key}")
        if result.deterministic_result:
            print(f"Deterministic report path: {result.deterministic_result.report_path}")
            print(f"Deterministic trace path: {result.deterministic_result.trace_path}")
        print(f"Agent report path: {result.agent_report_path}")
        print(f"Agent trace path: {result.agent_trace_path}")
        for warning in result.warnings:
            print(f"Warning: {warning}")
        for error in result.blocking_errors:
            print(f"Blocking error: {error}")
        return 0 if result.status == "completed" else 1

    if not args.key and not args.mapping:
        parser.error("deterministic mode requires either --key or --mapping")

    if args.llm_summary:
        print("Warning: --llm-summary is ignored in Milestone 4. LLM polish is planned for a later milestone.")

    from .reconciliation_engine import run_deterministic_reconciliation

    try:
        result = run_deterministic_reconciliation(
            source_path=args.source,
            target_path=args.target,
            output_dir=args.output_dir,
            key=args.key,
            mapping_path=args.mapping,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    for warning in result.warnings:
        print(f"Warning: {warning}")

    if result.blocking_errors:
        print("Deterministic reconciliation could not complete record-level comparison.")
    else:
        print("Deterministic reconciliation completed.")
    print(f"Key mode: {result.key_mode}")
    print(f"Source key: {result.source_key}")
    print(f"Target key: {result.target_key}")
    print(f"Source rows: {result.source_row_count}")
    print(f"Target rows: {result.target_row_count}")
    print(f"Matched keys: {result.matched_key_count}")
    print(f"Missing from target: {result.missing_in_target_count}")
    print(f"Unexpected in target: {result.unexpected_in_target_count}")
    if result.value_comparison_enabled:
        print("Value comparison: ran")
    else:
        reason = result.value_comparison_skipped_reason or "unknown reason"
        print(f"Value comparison: skipped - {reason}")
    print(f"Value mismatches: {result.value_mismatch_count}")
    print(f"Report path: {result.report_path}")
    print(f"Trace path: {result.trace_path}")
    if result.blocking_errors:
        for error in result.blocking_errors:
            print(f"Blocking error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
