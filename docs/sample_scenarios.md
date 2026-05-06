# Sample Reconciliation Scenarios

Milestone 2 supports record-level deterministic reconciliation for same-name keys only.

**Milestone 2 does not yet check mapped field values.**

## Milestone 2 key-presence scenarios

### Customers (`customer_id`)

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

### Orders (`order_id`)

- Source: `sample_data/orders/source_orders.csv`

### Clean migration
- Target: `sample_data/orders/target_orders_clean.csv`
- Expected: no missing keys, no unexpected keys, no duplicate target keys.

### Migration issues (record-level expectations)
- Target: `sample_data/orders/target_orders_migration_issues.csv`
- Expected missing ID: `ORD-9012`.
- Expected unexpected ID: `ORD-9999`.

## Future value-comparison fixture notes (not checked in Milestone 2)

- `target_customers_value_mismatches.csv` includes deliberate differences in email, status, phone, date, and balance fields.
- `target_orders_migration_issues.csv` also includes amount tolerance examples, a true amount mismatch, status casing differences, and date-format examples.
- CRM fixtures (`sample_data/crm_migration/*`) are future mapping-config scenarios because source and target key names differ.

## CRM migration (future mapping-config scenario)

CRM fixtures use different key names between source and target, so full reconciliation is deferred to Milestone 3 mapping-config implementation.


## Milestone 3 note
Mapping config now supports `entity`, `source_key`, `target_key`, and `field_mappings` validation for deterministic key resolution. Mapped field value comparison/comparator execution starts in Milestone 4.
