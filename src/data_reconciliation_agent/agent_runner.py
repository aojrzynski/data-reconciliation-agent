"""Agent-mode orchestration for bounded deterministic execution."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .intake import load_dataset
from .key_inference import infer_key_candidates
from .planner import AgentPlan, build_agent_plan
from .tools import run_reconciliation_tool


@dataclass(frozen=True)
class AgentRunResult:
    status: str
    deterministic_result: object | None
    agent_report_path: str
    agent_trace_path: str
    plan: AgentPlan
    warnings: list[str]
    blocking_errors: list[str]


def _confirm_assumptions(assumptions: list[str]) -> bool:
    print("Agent assumptions:")
    for assumption in assumptions:
        print(f"- {assumption}")
    response = input("Type y/yes to continue: ").strip().lower()
    return response in {"y", "yes"}


def run_agent_reconciliation(source_path: str, target_path: str, output_dir: str, key: str | None = None, mapping_path: str | None = None, confirm_assumptions: bool = False) -> AgentRunResult:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    source = load_dataset(source_path)
    target = load_dataset(target_path)
    key_candidates = [] if key or mapping_path else infer_key_candidates(source.dataframe, target.dataframe)
    plan = build_agent_plan(source.path, target.path, key, mapping_path, key_candidates)

    status = "completed"
    deterministic_result = None
    blocking_errors = list(plan.blocking_errors)
    warnings = list(plan.warnings)
    if plan.status == "blocked":
        status = "blocked"
    elif confirm_assumptions and plan.assumptions:
        if not _confirm_assumptions(plan.assumptions):
            status = "cancelled"
            blocking_errors.append("User declined inferred assumptions.")
        else:
            deterministic_result = run_reconciliation_tool(plan, output_dir)
    else:
        deterministic_result = run_reconciliation_tool(plan, output_dir)

    trace_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "agent",
        "source_path": source.path,
        "target_path": target.path,
        "inputs": {"key_provided": bool(key), "mapping_provided": bool(mapping_path), "confirm_assumptions": confirm_assumptions},
        "plan": {
            "status": plan.status,
            "key_mode": plan.key_mode,
            "source_key": plan.source_key,
            "target_key": plan.target_key,
            "mapping_path": plan.mapping_path,
            "assumptions": plan.assumptions,
            "warnings": plan.warnings,
            "blocking_errors": plan.blocking_errors,
            "planned_steps": plan.planned_steps,
        },
        "key_candidates": [asdict(c) for c in plan.key_candidates],
        "deterministic_run": {
            "executed": deterministic_result is not None,
            "report_path": getattr(deterministic_result, "report_path", None),
            "trace_path": getattr(deterministic_result, "trace_path", None),
            "matched_key_count": getattr(deterministic_result, "matched_key_count", None),
            "missing_in_target_count": getattr(deterministic_result, "missing_in_target_count", None),
            "unexpected_in_target_count": getattr(deterministic_result, "unexpected_in_target_count", None),
            "value_mismatch_count": getattr(deterministic_result, "value_mismatch_count", None),
        },
        "final_status": status,
    }
    agent_trace_path = str(out / "agent_trace.json")
    Path(agent_trace_path).write_text(json.dumps(trace_payload, indent=2), encoding="utf-8")

    report_lines = [
        "# Agent run summary",
        f"- Final status: {status}",
        "",
        "## Inputs",
        f"- Source: `{source.path}`",
        f"- Target: `{target.path}`",
        f"- Key provided: {bool(key)}",
        f"- Mapping provided: {bool(mapping_path)}",
        "",
        "## Plan",
        f"- Plan status: {plan.status}",
        f"- Key mode: {plan.key_mode}",
        "",
        "## Assumptions",
        *([f"- {a}" for a in plan.assumptions] or ["- None"]),
        "",
        "## Key/mapping decision",
        f"- Source key: {plan.source_key}",
        f"- Target key: {plan.target_key}",
        "",
        "## Deterministic run result",
        f"- Executed: {deterministic_result is not None}",
        "",
        "## Artifacts written",
        f"- Agent trace: `{agent_trace_path}`",
        f"- Agent report: `{out / 'agent_report.md'}`",
        "",
        "## What the agent did not do",
        "- The agent did not decide whether values matched. It selected a bounded execution plan and called the deterministic reconciliation engine.",
    ]
    if status != "completed":
        report_lines.extend(["", "## Blocking details", *[f"- {e}" for e in blocking_errors]])
    agent_report_path = str(out / "agent_report.md")
    Path(agent_report_path).write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return AgentRunResult(status, deterministic_result, agent_report_path, agent_trace_path, plan, warnings, blocking_errors)
