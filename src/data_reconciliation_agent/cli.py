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
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "agent":
        print("Agent mode is planned for a later milestone and is not implemented yet.")
        return 2

    if not args.source or not args.target or not args.key:
        parser.error("deterministic mode requires --source, --target, and --key")

    if args.mapping:
        print("Warning: --mapping is ignored in Milestone 2. Mapping config will be implemented in Milestone 3.")
    if args.llm_summary:
        print("Warning: --llm-summary is ignored in Milestone 2. LLM polish is planned for a later milestone.")

    from .reconciliation_engine import run_deterministic_reconciliation

    try:
        result = run_deterministic_reconciliation(args.source, args.target, args.key, args.output_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print("Deterministic reconciliation completed.")
    print(f"Source rows: {result.source_row_count}")
    print(f"Target rows: {result.target_row_count}")
    print(f"Matched keys: {result.matched_key_count}")
    print(f"Missing from target: {result.missing_in_target_count}")
    print(f"Unexpected in target: {result.unexpected_in_target_count}")
    print(f"Report path: {result.report_path}")
    print(f"Trace path: {result.trace_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
