# Sample Reconciliation Scenarios

Milestone 4 supports deterministic record-level reconciliation and mapped value comparison for:

- same-name keys via `--key`
- different source/target key names via mapping config (`--mapping`)

Mapped field values are compared only for records matched by key.

## Customers (`customer_id`)

- Source: `sample_data/customers/source_customers.csv`

### Clean migration
- Target: `sample_data/customers/target_customers_clean.csv`
- Expected: no missing keys, no unexpected keys, no duplicate target keys.

### Missing records
- Target: `sample_data/customers/target_customers_missing_records.csv`
- Expected missing IDs: `CUST-1003`, `CUST-1009`.

### Extra records
- Target: `sample_data/customers/target_customers_extra_records.csv`
- Expected unexpected IDs: `CUST-2013`, `CUST-2014`.

### Duplicate keys
- Target: `sample_data/customers/target_customers_duplicate_keys.csv`
- Expected duplicated target ID: `CUST-1006`.

## Orders (`order_id`)

- Source: `sample_data/orders/source_orders.csv`

### Clean migration
- Target: `sample_data/orders/target_orders_clean.csv`
- Expected: no missing keys, no unexpected keys, no duplicate target keys.

### Migration issues (record-level expectations)
- Target: `sample_data/orders/target_orders_migration_issues.csv`
- Expected missing ID: `ORD-9012`.
- Expected unexpected ID: `ORD-9999`.

## CRM migration (mapping-config key reconciliation)

CRM record-level reconciliation is now supported through mapping config.

- Source: `sample_data/crm_migration/source_contacts_salesforce.csv`
- Clean target: `sample_data/crm_migration/target_contacts_dynamics_clean.csv`
  - matched keys: `10`
  - missing from target: `0`
  - unexpected in target: `0`
- Issues target: `sample_data/crm_migration/target_contacts_dynamics_issues.csv`
  - missing source ID: `SF-007`
  - unexpected target `legacy_salesforce_id`: `SF-999`

CRM issue fixtures now include mapped value mismatches in `value_mismatches.csv`.
