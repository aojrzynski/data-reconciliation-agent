"""Rule-based planner for bounded agent mode."""

from __future__ import annotations

from dataclasses import dataclass

from .key_inference import KeyCandidate
from .mapping import load_mapping_config


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
    source_columns: list[str] | None = None,
    target_columns: list[str] | None = None,
) -> AgentPlan:
    # Planning precedence is explicit and deterministic:
    # mapping config -> explicit --key -> inferred same-name key -> blocked.
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
        # Mapping is the strongest signal because it explicitly defines source/target keys.
        mapping_config = load_mapping_config(mapping_path)
        key_mode = "mapping_config"
        source_key = mapping_config.source_key
        target_key = mapping_config.target_key
    elif key:
        # Explicit key is next: deterministic same-name key on both sides.
        key_mode = "explicit_same_name_key"
        source_key = target_key = key
    else:
        highs = [c for c in key_candidates if c.confidence == "high"]
        selected: KeyCandidate | None = None
        if len(highs) == 1:
            selected = highs[0]
        elif len(highs) > 1:
            # Tie-breaker: choose only when there is a clear score lead.
            # If not clear, prefer blocking over guessing to preserve auditability.
            best = highs[0]
            second = highs[1]
            if best.score > second.score + 0.10:
                selected = best
            else:
                if source_columns and target_columns and source_columns[0] == target_columns[0]:
                    # Conservative fallback: same first column and no weaker score.
                    first_column = source_columns[0]
                    first_column_match = next((c for c in highs if c.source_key == first_column and c.target_key == first_column), None)
                    if first_column_match is not None and first_column_match.score >= best.score:
                        selected = first_column_match

        if selected is not None:
            key_mode = "inferred_same_name_key"
            source_key = target_key = selected.source_key
            assumptions.append(f"Using inferred same-name key '{source_key}'.")
            warnings.extend(selected.warnings)
        else:
            errors.append("No safe key inference result. Provide --key or --mapping.")
            if len(highs) > 1:
                # Ambiguity blocks execution intentionally.
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
