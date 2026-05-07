# Example Commands

All commands are copy/paste-ready from repository root.

## Install

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -e ".[dev]"
```

Optional OpenAI polish dependencies:

```bash
pip install -e ".[dev,llm]"
```

## Run tests

```bash
python -m pytest
```

## Deterministic clean customer run

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --output-dir outputs/customers_clean_run
```

## Deterministic customer value mismatch run

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_value_mismatches.csv \
  --mapping config/examples/customers_value_mapping.yaml \
  --mode deterministic \
  --output-dir outputs/customers_value_mismatch_run
```

## Deterministic CRM mapping run

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts_salesforce.csv \
  --target sample_data/crm_migration/target_contacts_dynamics_clean.csv \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode deterministic \
  --output-dir outputs/crm_clean_run
```

## CRM issues run

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts_salesforce.csv \
  --target sample_data/crm_migration/target_contacts_dynamics_issues.csv \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode deterministic \
  --output-dir outputs/crm_issues_run
```

## Agent inferred customer key

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --mode agent \
  --output-dir outputs/customers_agent_inferred
```

## Agent inferred order key

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/orders/source_orders.csv \
  --target sample_data/orders/target_orders_clean.csv \
  --mode agent \
  --output-dir outputs/orders_agent_inferred
```

## Agent CRM mapping run

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/crm_migration/source_contacts_salesforce.csv \
  --target sample_data/crm_migration/target_contacts_dynamics_clean.csv \
  --mapping config/examples/crm_contacts_mapping.yaml \
  --mode agent \
  --output-dir outputs/crm_agent_run
```

## Deterministic fallback summary (no OpenAI required)

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --llm-summary \
  --output-dir outputs/customers_fallback_summary
```

## OpenAI summary (optional)

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"  # optional override
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --llm-summary \
  --output-dir outputs/customers_openai_summary
```

## Confirm-assumptions example

Use when agent mode reports blocked assumptions and you want explicit control:

```bash
python -m data_reconciliation_agent.cli \
  --source sample_data/customers/source_customers.csv \
  --target sample_data/customers/target_customers_clean.csv \
  --key customer_id \
  --mode deterministic \
  --output-dir outputs/customers_confirmed_key
```
