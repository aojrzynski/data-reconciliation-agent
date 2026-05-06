"""Bounded tool wrapper for deterministic reconciliation."""

from __future__ import annotations

from .planner import AgentPlan
from .reconciliation_engine import ReconciliationResult, run_deterministic_reconciliation


def run_reconciliation_tool(plan: AgentPlan, output_dir: str) -> ReconciliationResult:
    if plan.mapping_path:
        return run_deterministic_reconciliation(
            source_path=plan.source_path,
            target_path=plan.target_path,
            output_dir=output_dir,
            mapping_path=plan.mapping_path,
        )
    return run_deterministic_reconciliation(
        source_path=plan.source_path,
        target_path=plan.target_path,
        output_dir=output_dir,
        key=plan.source_key,
    )
