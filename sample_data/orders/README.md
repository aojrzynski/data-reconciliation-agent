# Orders Fixtures

Order migration fixtures focused on record-level and field-level reconciliation behavior.

Files:
- `source_orders.csv`: source order records
- `target_orders_clean.csv`: expected successful migration output
- `target_orders_migration_issues.csv`: intentionally includes missing/extra orders and value issues

The issues fixture includes:
- one missing order
- one unexpected order
- one amount difference within 0.01 tolerance
- one true amount mismatch
- one status casing difference
- one date formatting difference

Use with `config/examples/orders_mapping.yaml`.
