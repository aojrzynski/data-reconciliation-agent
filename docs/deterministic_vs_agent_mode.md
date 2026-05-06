# Deterministic vs Agent Mode

## Deterministic mode

Use deterministic mode when you already know binding inputs:
- `--key` for same-name record keys, or
- `--mapping` for different source/target key names and mapped field comparisons.

Flow:
1. CLI validates required arguments.
2. Deterministic engine runs reconciliation directly.
3. Canonical artifacts are written (`reconciliation_trace.json`, `reconciliation_report.md`, exception CSVs).

Deterministic outputs are the source of truth for match/mismatch outcomes.

## Agent mode (bounded, rule-based)

Agent mode does **not** replace deterministic checks. It only coordinates them.

Flow:
1. CLI calls `agent_runner`.
2. Planner resolves bounded assumptions:
   - mapping wins when provided,
   - explicit key used when provided,
   - otherwise same-name key inference is attempted.
3. If plan is runnable, tools wrapper calls deterministic engine.
4. Agent artifacts are written (`agent_trace.json`, `agent_report.md`) to explain plan decisions.

If key inference is ambiguous, agent mode blocks safely and asks for `--key` or `--mapping`.

## Authority boundary

- Agent mode does **not** decide value equality.
- Deterministic engine does decide value equality, based on explicit comparators and mappings.
- Agent trace explains orchestration decisions and evidence collected.


## Optional LLM polish layer

Flow boundary: deterministic engine writes authoritative evidence first, agent mode orchestrates, and optional LLM polish produces a readability-only `llm_summary.md` (deterministic fallback when no external provider is available).

The LLM polish layer does not perform reconciliation and is never authoritative.
