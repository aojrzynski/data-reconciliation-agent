# How It Works

This project is designed around a simple split:

1. deterministic reconciliation checks do the real validation
2. agent mode coordinates deterministic tools and summarizes outputs

Phase 0 does not implement reconciliation logic yet. It defines the contract so future milestones can add behavior without design drift.


## Milestone 5 Agent Mode

Agent mode is now implemented as a bounded orchestration layer. It resolves key/mapping assumptions, writes `agent_trace.json` and `agent_report.md`, and then calls the deterministic engine. Deterministic outputs remain authoritative.
