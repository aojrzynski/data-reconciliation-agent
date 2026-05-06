# Project Scope (V1)

## In scope for V1

- Local-first CLI workflow for one source file vs one target file
- CSV and XLSX input handling
- One logical entity/table per run
- Optional explicit key input
- Optional key inference fallback
- Optional mapping YAML input
- Deterministic reconciliation checks:
  - row counts
  - column summaries
  - key existence
  - null keys
  - duplicate keys
  - missing records in target
  - unexpected records in target
  - mapped value mismatches
  - basic string/number/date comparisons
  - null handling rules
- Output artifacts:
  - JSON trace
  - markdown report
  - exception CSV files
- Agent mode for bounded orchestration around deterministic tools
- Optional LLM summary polish for report readability only

## Out of scope for V1

- Multi-entity orchestration in one run
- Real-time streaming reconciliation
- Complex fuzzy matching and probabilistic entity resolution
- Auto-remediation or direct write-back into source/target systems
- Distributed job execution platform
- Full BI semantic layer integration
- LLM as reconciliation authority

## Design principles

- Deterministic checks are source of truth
- Local-first and CLI-first by default
- Keep behavior explicit, auditable, and testable
- Favor readable code over clever abstractions
- Keep outputs useful for investigation and handoff
- Prefer plain language documentation over marketing language

## Success criteria for V1

V1 is successful when a user can:

1. Run a single command against source and target files.
2. Produce deterministic reconciliation results they can audit.
3. Inspect exception records with concrete evidence.
4. Understand what failed and why from trace + report artifacts.
5. Re-run the same inputs and get the same deterministic results.
