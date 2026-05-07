"""Thin tool boundary used by agent mode.

The planner decides what to run. This module forwards that decision to the
deterministic engine, which remains the evidence-producing authority.
"""

from __future__ import annotations

from .planner import AgentPlan
from .reconciliation_engine import ReconciliationResult, run_deterministic_reconciliation


def run_reconciliation_tool(plan: AgentPlan, output_dir: str) -> ReconciliationResult:
    """Execute reconciliation according to the agent plan without adding logic.

    In mapping mode we pass only ``mapping_path`` so mapping-owned keys are used
    directly and explicit-key warnings are not triggered by inferred values.
    """
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
