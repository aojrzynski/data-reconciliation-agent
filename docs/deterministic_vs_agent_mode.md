# Deterministic vs Agent Mode

## Deterministic mode

Deterministic mode runs explicit reconciliation checks. Its outputs are authoritative.

## Agent mode

Agent mode plans and coordinates deterministic checks. It can improve run ergonomics and summarization, but it is not the authority for data match decisions.


## Milestone 5 Agent Mode

Agent mode is now implemented as a bounded orchestration layer. It resolves key/mapping assumptions, writes `agent_trace.json` and `agent_report.md`, and then calls the deterministic engine. Deterministic outputs remain authoritative.
