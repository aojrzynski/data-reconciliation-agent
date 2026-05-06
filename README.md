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

**Milestone 3 implemented / mapping config support**: the CLI supports record-level deterministic reconciliation using either an explicit same-name key (`--key`) or a YAML mapping file (`--mapping`) with `source_key` and `target_key`. Mapping config is currently used for key resolution and validation only. Mapped field value comparison starts in Milestone 4.

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

## Example working CLI commands

Same-name key reconciliation:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --output-dir outputs/customers_clean_run
```

Mapping-based reconciliation:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts_salesforce.csv \
  --target sample_data/crm_migration/target_contacts_dynamics_clean.csv \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode deterministic \
  --output-dir outputs/crm_clean_run
```

## Non-goals (v1)

- building a fully autonomous general-purpose data agent
- replacing deterministic checks with LLM judgments
- distributed/cloud-first orchestration
- heavy framework coupling
- full cross-table relational reconciliation in first release

## Fixture datasets for milestone development

The repository includes realistic fixture families that support current and future milestones:

- `sample_data/` for source/target CSV scenarios
- `config/examples/` for mapping YAML examples that match those fixtures
- `docs/sample_scenarios.md` for expected high-level outcomes by scenario

## Repository structure summary

- `src/data_reconciliation_agent/`: CLI and module skeletons
- `config/`: default rules and mapping examples
- `sample_data/`: scenario folders for fixtures
- `outputs/`: output artifact destination
- `docs/`: practical implementation and usage guides
- `tests/`: automated test coverage

## Current scope limits

- Field-level mapped value comparison is not implemented yet.
- Comparator execution is not implemented yet.
- Agent mode is not implemented yet.
- LLM summary polish is not implemented yet.
