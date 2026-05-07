# Data Reconciliation Agent

Data Reconciliation Agent is a local-first, CLI-first Python project for validating whether a **target dataset preserved what mattered from a source dataset**.

## Relationship to Data Quality Triage Agent

- Data Quality Triage Agent asks: **"What looks wrong inside one dataset?"**
- Data Reconciliation Agent asks: **"Did the target preserve what mattered from the source?"**

## Problem this solves

Teams doing migration or re-platforming work need source-to-target evidence, not intuition. Typical scenarios include:
- CRM migration validation,
- CSV export to target extract comparison,
- legacy-to-modern system data preservation checks.

The goal is clear deterministic evidence about what matched, what was missing, and what changed.

## Why deterministic checks are authoritative

- **Repeatable**: same inputs produce same outputs.
- **Testable**: behavior is covered with deterministic tests.
- **Auditable**: traces and exception artifacts are explicit.
- **Bounded agent role**: agent mode coordinates execution but does not judge value equality.

## Current status

**Milestone 6 implemented (current): optional LLM polish.**

- Deterministic reconciliation engine remains authoritative.
- Agent mode now works and coordinates bounded planning + deterministic execution.
- Agent mode writes `agent_trace.json` and `agent_report.md` in addition to deterministic artifacts.

## What agent mode does and does not do

Agent mode **does**:
- require source and target inputs,
- resolve key/mapping strategy using explicit rules,
- attempt bounded same-name key inference when key/mapping is not provided,
- block safely when inference is ambiguous,
- call deterministic reconciliation when plan is runnable,
- record assumptions, warnings, blocking reasons, and execution artifacts.

Agent mode **does not**:
- decide whether values match,
- replace deterministic reconciliation logic,
- use fuzzy matching,
- auto-correct data,
- require an LLM.

## Example CLI commands

Deterministic same-name key run:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --output-dir outputs/customers_clean_run
```

Deterministic mapping run:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts_salesforce.csv \
  --target sample_data/crm_migration/target_contacts_dynamics_clean.csv \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode deterministic \
  --output-dir outputs/crm_clean_run
```

Agent mode run:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_value_mismatches.csv \
  --mode agent \
  --output-dir outputs/customers_agent_run
```

## Non-goals (v1)

- autonomous generalized agent behavior
- replacing deterministic checks with model judgment
- adding heavy agent frameworks
- fuzzy matching and auto-correction

## Repository structure

- `src/data_reconciliation_agent/`: implementation
- `config/`: default rules and mapping examples
- `sample_data/`: fixture datasets
- `docs/`: usage and architecture guides
- `tests/`: automated tests

## Fixtures and scenario pointers

- `sample_data/`: source/target fixture families
- `config/examples/`: mapping examples aligned to fixtures
- `docs/sample_scenarios.md`: expected scenario outcomes for learning and verification


Optional LLM summary (`--llm-summary`) is non-authoritative, uses only deterministic trace metadata, does not inspect raw datasets or exception row contents, and never replaces deterministic outputs. By default it writes a deterministic fallback summary; external provider polish with OpenAI is optional.

To enable optional OpenAI polish:

```bash
pip install -e ".[dev,llm]"
export OPENAI_API_KEY="..."
# optional model override
export OPENAI_MODEL="gpt-4o-mini"
```

If `OPENAI_API_KEY` is not set, or OpenAI is unavailable, `--llm-summary` still works offline via deterministic fallback.

Example with optional summary:
```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --llm-summary \
  --output-dir outputs/customers_with_llm_summary
```
