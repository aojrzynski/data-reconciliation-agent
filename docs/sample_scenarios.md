# Sample Reconciliation Scenarios

Milestone 4 supports deterministic record-level reconciliation and mapped value comparison for:
- same-name keys via `--key`
- different source/target key names via mapping config (`--mapping`)

Mapped value comparison only runs for records matched by key.

## Customers (`customer_id`)

- Source: `sample_data/customers/source_customers.csv`

### Clean migration
- Target: `sample_data/customers/target_customers_clean.csv`
- Expected: no missing keys, no unexpected keys, no duplicate target keys.
- With mapping: value comparison runs and should **not** write `value_mismatches.csv`.

### Value mismatch fixture
- Target: `sample_data/customers/target_customers_value_mismatches.csv`
- Expected: writes `value_mismatches.csv`.
- Includes deliberate mismatches for email, status, phone, date, and balance.

### Missing records
- Target: `sample_data/customers/target_customers_missing_records.csv`
- Expected missing IDs: `CUST-1003`, `CUST-1009`.

### Extra records
- Target: `sample_data/customers/target_customers_extra_records.csv`
- Expected unexpected IDs: `CUST-2013`, `CUST-2014`.

### Duplicate keys
- Target: `sample_data/customers/target_customers_duplicate_keys.csv`
- Expected duplicated target ID: `CUST-1006`.
- Value comparison should be skipped because duplicate keys make row lookup ambiguous.

## Orders (`order_id`)

- Source: `sample_data/orders/source_orders.csv`
- Target: `sample_data/orders/target_orders_migration_issues.csv`
- Expected missing ID: `ORD-9012`.
- Expected unexpected ID: `ORD-9999`.
- `ORD-9006` amount `1000.00` vs `1000.009` should match (tolerance `0.01`).
- `ORD-9007` amount `42.00` vs `45.00` should mismatch.
- `ORD-9002` status casing difference should match.
- `ORD-9004` date format difference should match.

## CRM migration (mapping-config key reconciliation)

- Source: `sample_data/crm_migration/source_contacts_salesforce.csv`
- Issues target: `sample_data/crm_migration/target_contacts_dynamics_issues.csv`
- Expected missing source ID: `SF-007`.
- Expected unexpected target `legacy_salesforce_id`: `SF-999`.
- `value_mismatches.csv` should include:
  - email mismatch for `SF-002`
  - phone mismatch for `SF-003`
  - status/statecode mismatch for `SF-004`
  - owner mismatch for `SF-006`
- Date format difference for `SF-005` should match and should not appear as mismatch.
