# Customers Fixtures

Customer migration fixtures that model a common source-to-target column rename pattern.

Files:
- `source_customers.csv`: source system records
- `target_customers_clean.csv`: correctly migrated target records
- `target_customers_missing_records.csv`: target omits some source customers
- `target_customers_extra_records.csv`: target includes unexpected customers
- `target_customers_value_mismatches.csv`: target includes field-level mismatches
- `target_customers_duplicate_keys.csv`: target includes duplicated `customer_id`

Use with `config/examples/customers_mapping.yaml`.
