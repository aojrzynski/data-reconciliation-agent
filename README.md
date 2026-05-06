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

**Phase 0 foundation**: project contract, architecture docs, folder structure, and light code skeleton are in place. Real reconciliation logic is intentionally not implemented yet.

## Planned v1 features

- source and target row/column checks
- key existence, null key, and duplicate key checks
- missing and unexpected record detection
- mapping-based field comparisons
- basic string/number/date comparators with null handling
- JSON trace outputs
- markdown reconciliation report
- exception CSV outputs
- optional LLM-polished summary (non-authoritative)

## Example future CLI commands

These represent intended usage once deterministic engine milestones are complete:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers.csv \
  --key customer_id \
  --mapping config/examples/customers_mapping.yaml \
  --mode deterministic \
  --output-dir outputs/customers_run
```

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts.xlsx \
  --target sample_data/crm_migration/target_contacts.xlsx \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode agent \
  --llm-summary
```

## Non-goals (v1)

- building a fully autonomous general-purpose data agent
- replacing deterministic checks with LLM judgments
- distributed/cloud-first orchestration
- heavy framework coupling
- full cross-table relational reconciliation in first release

## Repository structure summary

- `src/data_reconciliation_agent/`: CLI and module skeletons
- `config/`: default rules and mapping examples
- `sample_data/`: scenario folders for future fixtures
- `outputs/`: output artifact destination
- `docs/`: practical implementation and usage guides
- `tests/`: lightweight automated test coverage

## Learning angle

This repository is designed to be understandable by technical recruiters, developers, analysts, and engineers learning bounded agent patterns. The writing is intentionally direct so readers can quickly see what is deterministic, what is orchestration, and where future milestones fit.
