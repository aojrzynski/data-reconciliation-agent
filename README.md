# Data Reconciliation Agent

Data Reconciliation Agent is a local-first, CLI-first Python project for validating whether a **target dataset preserved what mattered from a source dataset**.

This project follows the same practical philosophy as the earlier Data Quality Triage Agent, but focuses on a different question:

- Data Quality Triage Agent: "What looks wrong inside one dataset?"
- Data Reconciliation Agent: "Did the target dataset correctly preserve the important parts of the source dataset?"

## Problem this solves

Teams migrating or re-platforming data need evidence, not intuition. This project is built for source-to-target validation workflows like:

- Salesforce to Dynamics migration
- CSV export to warehouse extract validation
- Legacy report to new report comparison
- Pre-migration vs post-migration checks

## Why deterministic checks are authoritative

Deterministic checks are the source of truth in this project because they are:

- repeatable
- testable
- auditable
- easy to explain to technical and non-technical stakeholders

The core matching and mismatch detection logic belongs in deterministic code, not in model output.

## What agent mode will eventually do

Agent mode is an orchestration layer, not a replacement for deterministic reconciliation.

Planned responsibilities for agent mode:

- guide intake assumptions
- coordinate mapping and key handling
- choose bounded, deterministic tool steps
- summarize findings and open questions

Agent mode will not "decide by vibe" whether records match.

## Current status

**Milestone 2 implemented / deterministic reconciliation v0**: the CLI now performs record-level deterministic source-to-target reconciliation using an explicit same-name key column. It writes a JSON trace, markdown report, and exception CSV outputs for missing, unexpected, null-key, and duplicate-key findings.

## Planned v1 features

- source and target row/column checks
- key existence, null key, and duplicate key checks
- missing and unexpected record detection
- mapping-based field comparisons
- basic string/number/date/datetime comparators with null handling
- JSON trace outputs
- markdown reconciliation report
- exception CSV outputs
- optional LLM-polished summary (non-authoritative)

## Example working CLI command (Milestone 2)

This command works now for record-level reconciliation with same-name keys:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --output-dir outputs/customers_clean_run
```


## Non-goals (v1)

- building a fully autonomous general-purpose data agent
- replacing deterministic checks with LLM judgments
- distributed/cloud-first orchestration
- heavy framework coupling
- full cross-table relational reconciliation in first release


## Fixture datasets for milestone development

The repository now includes realistic fixture families that support current and future milestones:

- `sample_data/` for source/target CSV scenarios
- `config/examples/` for mapping YAML examples that match those fixtures
- `docs/sample_scenarios.md` for expected high-level outcomes by scenario

These datasets are fixtures for implementation and testing. They do not imply the reconciliation engine is complete yet.

## Repository structure summary

- `src/data_reconciliation_agent/`: CLI and module skeletons
- `config/`: default rules and mapping examples
- `sample_data/`: scenario folders for future fixtures
- `outputs/`: output artifact destination
- `docs/`: practical implementation and usage guides
- `tests/`: lightweight automated test coverage

## Learning angle

This repository is designed to be understandable by technical recruiters, developers, analysts, and engineers learning bounded agent patterns. The writing is intentionally direct so readers can quickly see what is deterministic, what is orchestration, and where future milestones fit.


## Milestone 2 scope limits

- Mapping config execution is not implemented yet (planned for Milestone 3).
- Field-level mapped value comparison is not implemented yet.
- Agent mode is not implemented yet.
- LLM summary polish is not implemented yet.


## Milestone 3 note
Mapping config now supports `entity`, `source_key`, `target_key`, and `field_mappings` validation for deterministic key resolution. Mapped field value comparison/comparator execution starts in Milestone 4.
