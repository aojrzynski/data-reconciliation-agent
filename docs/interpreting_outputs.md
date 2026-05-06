# Interpreting Outputs

## Deterministic artifacts (canonical)

- `reconciliation_trace.json`: machine-readable deterministic run evidence.
- `reconciliation_report.md`: human-readable deterministic summary.
- Exception CSVs: concrete rows for missing/unexpected/duplicate/null key and value mismatches.

Use these artifacts for final reconciliation conclusions.

- `llm_summary.md` (optional): readability-only summary from deterministic metadata. It is not evidence and must be validated against `reconciliation_trace.json` and exception CSVs.

## Agent artifacts (orchestration context)

### `agent_trace.json`

Key sections:
- top-level run context (`mode`, paths, inputs)
- `plan` (status, key mode, assumptions, warnings, blocking errors, planned steps)
- `key_candidates` (when inference was attempted)
- `deterministic_run` summary (executed flag + deterministic artifact paths and counts)
- top-level `warnings` and `blocking_errors`
- `final_status`

### `agent_report.md`

Human-readable explanation of:
- final status and plan status
- key/mapping decision
- assumptions, warnings, blocking errors
- planned steps
- deterministic artifact paths and counts when executed
- explicit authority boundary statement

## Relationship between artifact types

- Agent artifacts explain **how the run was orchestrated**.
- Deterministic artifacts show **what the deterministic engine concluded**.
- When they differ in tone/detail, deterministic artifacts remain authoritative.
