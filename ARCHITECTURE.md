# Architecture

## Runtime flow

`CLI -> agent_runner -> planner -> tools -> deterministic engine -> reports/traces`

Deterministic mode is a direct path from CLI to deterministic engine. Agent mode uses the full orchestration path above.

## Component responsibilities

1. **CLI (`cli.py`)**
   - parse arguments and dispatch mode.
2. **Agent runner (`agent_runner.py`)**
   - orchestrate bounded agent run lifecycle.
3. **Planner (`planner.py`)**
   - resolve mapping/key strategy and produce explicit plan/assumptions.
4. **Tools wrapper (`tools.py`)**
   - call deterministic reconciliation engine with resolved plan inputs.
5. **Deterministic engine (`reconciliation_engine.py`)**
   - authoritative reconciliation logic and canonical deterministic artifacts.

## Authority boundary

Agent layer coordinates execution and documents assumptions.
It does not decide whether values match.
Deterministic outputs remain authoritative.
