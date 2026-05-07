# Data Reconciliation Agent

Data Reconciliation Agent is a local-first, CLI-first Python project for checking whether a target dataset preserved what mattered from a source dataset. It is built for migration, re-platforming, and source-to-target validation work where you need evidence, not guesswork.

## Why this exists

Migration work usually fails in boring ways:
- rows go missing,
- extra rows show up,
- key fields do not line up,
- values change during transforms,
- and people sign off based on spreadsheet spot checks.

This project gives deterministic outputs you can rerun, inspect, and review.

## Why not just ask an LLM?

LLMs are useful for summarising findings, but reconciliation should not depend on model judgement.

For repetitive, rules-heavy checks, deterministic code is usually cheaper, faster, and more accurate than asking a model to reason over the task each run. A good use of AI here is helping build and explain a reliable deterministic tool, not redoing deterministic reconciliation decisions every time.

This boundary matters when token cost, repeatability, auditability, and data handling are important.

Authority boundary in this repo:
- deterministic engine = evidence
- agent mode = orchestration
- LLM summary = readability only

The optional LLM layer reads structured deterministic metadata, not raw dataset rows, and trace/report/exception artifacts remain the source of truth.

## Why I built it this way

I wanted to understand agents by building one from the inside out, starting with deterministic reconciliation that can stand on its own.

I deliberately separated responsibilities:
- deterministic reconciliation does the evidence-producing checks
- agent mode handles orchestration and assumption management
- optional LLM summary improves readability only

This is a learning project written so other people can follow the architecture without hidden automation.

The goal is not to make an LLM perform reconciliation. The goal is to show where an agent helps around reliable deterministic tools.

## What this project demonstrates

- source-to-target reconciliation for CSV/XLSX files
- YAML mapping config for different source/target key names and field names
- deterministic string/number/date/datetime comparators
- exception CSV outputs for missing/unexpected/duplicate/null/value mismatch cases
- bounded agent mode that plans and records assumptions
- optional OpenAI polish with deterministic fallback
- auditable trace/report artifacts

## Why this is an agent

Deterministic mode runs directly from user-provided key/mapping inputs.

Agent mode does bounded orchestration:
- inspects inputs,
- resolves key and mapping strategy,
- infers safe same-name keys when possible,
- blocks when assumptions are unsafe,
- then calls deterministic tools.

The agent coordinates work. It does not judge whether values match.

## Quick start

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -e ".[dev]"
```

Optional OpenAI polish dependencies:

```bash
pip install -e ".[dev,llm]"
```

## Example commands

1) Deterministic same-name key:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --output-dir outputs/customers_clean_run
```

2) Deterministic mapping with value mismatches:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts_salesforce.csv \
  --target sample_data/crm_migration/target_contacts_dynamics_issues.csv \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode deterministic \
  --output-dir outputs/crm_issues_run
```

3) Agent mode inferred key:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/orders/source_orders.csv \
  --target sample_data/orders/target_orders_clean.csv \
  --mode agent \
  --output-dir outputs/orders_agent_inferred
```

4) Agent mode with mapping:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts_salesforce.csv \
  --target sample_data/crm_migration/target_contacts_dynamics_clean.csv \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode agent \
  --output-dir outputs/crm_agent_mapping
```

5) Optional deterministic fallback summary:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --llm-summary \
  --output-dir outputs/customers_fallback_summary
```

6) Optional OpenAI summary:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"  # optional
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --llm-summary \
  --output-dir outputs/customers_openai_summary
```

## Output artifacts

Deterministic artifacts (evidence):
- `reconciliation_trace.json`
- `reconciliation_report.md`
- exception CSVs (`missing_in_target.csv`, `unexpected_in_target.csv`, etc.)

Agent artifacts (orchestration context):
- `agent_trace.json`
- `agent_report.md`

Optional readability layer:
- `llm_summary.md`

Authority boundary:
- deterministic artifacts are evidence,
- agent artifacts explain orchestration,
- LLM summary is readability-only.

## Project structure

- `src/data_reconciliation_agent/` core code (CLI, deterministic engine, planner, reports, optional LLM polish)
- `config/examples/` mapping examples
- `sample_data/` fixture datasets
- `docs/` usage, architecture, and extension guides
- `tests/` deterministic and orchestration test suite

## Run tests

```bash
python -m pytest
```

## Limitations and non-goals

- no fuzzy matching
- no auto-correction
- no database integration in v1
- no web UI
- not a full migration platform
- LLM output is non-authoritative
- same-name key inference is deliberately cautious

## Further reading

- `ARCHITECTURE.md`
- `PROJECT_SCOPE.md`
- `docs/how_it_works.md`
- `docs/interpreting_outputs.md`
- `docs/example_commands.md`
- `docs/extension_paths.md`
- `docs/adding_a_new_comparator.md`
- `FUTURE_WORK.md`
