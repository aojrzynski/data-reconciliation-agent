# Roadmap

## Milestone 0: Project foundation (implemented)
- repository scaffolding
- core docs and architecture contract
- CLI argument surface
- module skeletons and baseline tests

## Milestone 1: Fixtures and expected scenarios (implemented)
- source/target fixtures for customers, orders, and CRM contacts
- expected outcomes for happy and failure paths
- scenario-driven test harness

## Milestone 2: Deterministic reconciliation v0 (implemented)
- file intake and loading for CSV/XLSX
- key existence/null/duplicate checks
- missing and unexpected record detection

## Milestone 3: Mapping config (implemented)
- YAML mapping parser and validator
- source/target key resolution via mapping config
- mapped column validation and trace metadata

## Milestone 4: Value comparators and mapped field comparison (implemented)
- string/number/date/datetime comparators
- mapped field value comparison for matched keys
- mismatch summaries and exception output

## Milestone 5: Bounded agent mode orchestration (implemented / current)
- rule-based planner and explicit planned steps
- bounded key inference for same-name keys
- safe blocking on ambiguous assumptions
- deterministic tool orchestration wrapper
- `agent_trace.json` and `agent_report.md`

## Milestone 6: Optional LLM polish (planned)
- optional readability pass for reports
- explicit non-authoritative annotation
- deterministic outputs remain canonical

## Milestone 7: Hardening and teaching polish (planned)
- stronger edge-case coverage
- deeper documentation walkthroughs
- additional sample scenarios
