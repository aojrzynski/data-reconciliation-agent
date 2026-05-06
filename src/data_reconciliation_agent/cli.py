"""CLI entrypoint for the Data Reconciliation Agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .llm_summary import LLMSummaryResult, generate_llm_summary


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

        try:
            result = run_agent_reconciliation(
                source_path=args.source,
                target_path=args.target,
                output_dir=args.output_dir,
                key=args.key,
                mapping_path=args.mapping,
                confirm_assumptions=args.confirm_assumptions,
                llm_summary_requested=args.llm_summary,
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
        llm_result: LLMSummaryResult | None = None
        if args.llm_summary:
            if result.deterministic_result:
                llm_result = generate_llm_summary(result.deterministic_result.trace_path, args.output_dir)
            else:
                llm_result = LLMSummaryResult(
                    enabled=True,
                    generated=False,
                    skipped_reason="deterministic reconciliation did not execute",
                    provider=None,
                    output_path=None,
                    warnings=[],
                )
            if llm_result.generated:
                print(f"LLM summary: generated at {llm_result.output_path}")
            else:
                print(f"LLM summary: skipped - {llm_result.skipped_reason}")
        for warning in result.warnings:
            print(f"Warning: {warning}")
        for error in result.blocking_errors:
            print(f"Blocking error: {error}")
        if args.llm_summary:
            agent_trace = Path(result.agent_trace_path)
            payload = json.loads(agent_trace.read_text(encoding="utf-8"))
            payload["llm_summary"] = llm_result.__dict__
            agent_trace.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            report_path = Path(result.agent_report_path)
            existing = report_path.read_text(encoding="utf-8")
            report_path.write_text(
                existing
                + "\n## Optional LLM summary\n"
                + f"- Generated: {llm_result.generated}\n"
                + f"- Provider: {llm_result.provider}\n"
                + f"- Output path: {llm_result.output_path}\n"
                + f"- Skipped reason: {llm_result.skipped_reason}\n"
                + "- Non-authoritative: deterministic artifacts remain source of truth.\n",
                encoding="utf-8",
            )
        return 0 if result.status == "completed" else 1

    if not args.key and not args.mapping:
        parser.error("deterministic mode requires either --key or --mapping")

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
    if args.llm_summary:
        llm_result = generate_llm_summary(result.trace_path, args.output_dir)
        if llm_result.generated:
            print(f"LLM summary: generated at {llm_result.output_path}")
        else:
            print(f"LLM summary: skipped - {llm_result.skipped_reason}")
        trace_path = Path(result.trace_path)
        trace_data = json.loads(trace_path.read_text(encoding="utf-8"))
        trace_data["llm_summary"] = llm_result.__dict__ | {"requested": True}
        trace_path.write_text(json.dumps(trace_data, indent=2, sort_keys=True), encoding="utf-8")
        report_path = Path(result.report_path)
        report_path.write_text(
            report_path.read_text(encoding="utf-8")
            + "\n## Optional LLM summary\n"
            + f"- Generated: {llm_result.generated}\n"
            + f"- Provider: {llm_result.provider}\n"
            + f"- Output path: {llm_result.output_path}\n"
            + f"- Skipped reason: {llm_result.skipped_reason}\n"
            + "- Non-authoritative: deterministic artifacts remain source of truth.\n",
            encoding="utf-8",
        )
    if result.blocking_errors:
        for error in result.blocking_errors:
            print(f"Blocking error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
