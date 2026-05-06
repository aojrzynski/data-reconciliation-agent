"""Rule-based planner for bounded agent mode."""

from __future__ import annotations

from dataclasses import dataclass

from .key_inference import KeyCandidate


@dataclass(frozen=True)
class AgentPlan:
    status: str
    mode: str
    source_path: str
    target_path: str
    key_mode: str | None
    source_key: str | None
    target_key: str | None
    mapping_path: str | None
    assumptions: list[str]
    warnings: list[str]
    blocking_errors: list[str]
    planned_steps: list[dict]
    key_candidates: list[KeyCandidate]


def build_agent_plan(
    source_path: str,
    target_path: str,
    key: str | None,
    mapping_path: str | None,
    key_candidates: list[KeyCandidate],
) -> AgentPlan:
    steps = [
        {"step": "load source dataset"},
        {"step": "load target dataset"},
        {"step": "inspect schema"},
        {"step": "resolve key/mapping assumptions"},
        {"step": "run deterministic reconciliation"},
        {"step": "write deterministic report/trace"},
        {"step": "write agent report/trace"},
    ]
    assumptions: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    key_mode = source_key = target_key = None

    if mapping_path:
        key_mode = "mapping_config"
    elif key:
        key_mode = "explicit_same_name_key"
        source_key = target_key = key
    else:
        highs = [c for c in key_candidates if c.confidence == "high"]
        if len(highs) == 1:
            key_mode = "inferred_same_name_key"
            source_key = target_key = highs[0].source_key
            assumptions.append(f"Using inferred same-name key '{source_key}'.")
            warnings.extend(highs[0].warnings)
        else:
            errors.append("No safe key inference result. Provide --key or --mapping.")
            if len(highs) > 1:
                warnings.append("Multiple high-confidence key candidates were found and cannot be auto-selected safely.")

    status = "blocked" if errors else "runnable"
    return AgentPlan(
        status=status,
        mode="agent",
        source_path=source_path,
        target_path=target_path,
        key_mode=key_mode,
        source_key=source_key,
        target_key=target_key,
        mapping_path=mapping_path,
        assumptions=assumptions,
        warnings=warnings,
        blocking_errors=errors,
        planned_steps=steps,
        key_candidates=key_candidates,
    )
