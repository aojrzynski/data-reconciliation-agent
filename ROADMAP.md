# Roadmap

## Milestone 0: Project foundation

- repository scaffolding
- core docs and architecture contract
- CLI argument surface
- module skeletons and baseline tests

## Milestone 1: Fixtures and expected scenarios

- small source/target fixtures for customers, orders, CRM contacts
- expected outputs for happy path and failure path checks
- test harness for scenario-driven development

## Milestone 2: Deterministic reconciliation v0

- file intake and table-like loading for CSV/XLSX
- row and column summary checks
- key existence/null/duplicate checks
- missing and unexpected record detection

## Milestone 3: Mapping config

- YAML mapping parser and validator
- source-to-target field alignment rules
- per-field comparison rule selection

## Milestone 4: Value comparators

- string comparator
- numeric comparator with tolerance
- date comparator
- null-handling comparator behavior

## Milestone 5: Agent mode

- deterministic tool orchestration flow
- bounded planning and run coordination
- transparent assumptions and execution plan output

## Milestone 6: Optional LLM polish

- optional report readability pass
- explicit non-authoritative annotation
- deterministic output remains canonical

## Milestone 7: Hardening and teaching polish

- error handling cleanup
- stronger tests and edge cases
- documentation walkthrough improvements
- portfolio-ready examples and usage notes
