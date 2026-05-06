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

**Milestone 4 implemented / mapped value comparison support**: deterministic reconciliation now runs record-level key matching and mapped field value comparison for matched keys when `--mapping` is provided, including comparator execution, value mismatch exceptions, and value comparison trace/report sections.

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

- Agent mode is not implemented yet.
- LLM summary polish is not implemented yet.


## Learning angle

This repository is intended to be useful as both a small reconciliation tool and a learning repo for bounded data-agent architecture. The deterministic engine does the evidence-producing work; later agent mode will coordinate deterministic tools rather than replace them.


## Milestone 5 Agent Mode

Agent mode is now implemented as a bounded orchestration layer. It resolves key/mapping assumptions, writes `agent_trace.json` and `agent_report.md`, and then calls the deterministic engine. Deterministic outputs remain authoritative.


### Agent mode example

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_value_mismatches.csv \
  --mode agent \
  --output-dir outputs/customers_agent_run
```
