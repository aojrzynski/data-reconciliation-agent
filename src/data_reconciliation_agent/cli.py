"""CLI entrypoint for the Data Reconciliation Agent."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data-reconciliation-agent",
        description=(
            "Phase 0 foundation CLI for source-to-target data reconciliation. "
            "Deterministic reconciliation logic will be implemented in later milestones."
        ),
    )
    parser.add_argument("--source", help="Path to source dataset file (CSV or XLSX).")
    parser.add_argument("--target", help="Path to target dataset file (CSV or XLSX).")
    parser.add_argument("--key", help="Optional explicit key column.")
    parser.add_argument("--mapping", help="Optional YAML mapping file path.")
    parser.add_argument(
        "--mode",
        choices=["deterministic", "agent"],
        default="deterministic",
        help="Execution mode. Default is deterministic.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Output directory for trace/report/exception artifacts.",
    )
    parser.add_argument(
        "--llm-summary",
        action="store_true",
        help="Request optional LLM report polish once available.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    print("Data Reconciliation Agent - Phase 0 foundation")
    print("No deterministic reconciliation logic is implemented yet.")
    print("This milestone establishes project structure, docs, and CLI contract.")
    print(f"Mode: {args.mode}")
    print(f"Source: {args.source}")
    print(f"Target: {args.target}")
    print(f"Key: {args.key}")
    print(f"Mapping: {args.mapping}")
    print(f"Output directory: {args.output_dir}")
    print(f"LLM summary requested: {args.llm_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
