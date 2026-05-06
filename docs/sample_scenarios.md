# Sample Reconciliation Scenarios

This document explains the fixture datasets used to validate future deterministic reconciliation logic.

These files are test fixtures and learning assets. They are not proof that reconciliation is implemented.

## Customers

- Source file: `sample_data/customers/source_customers.csv`
- Mapping file: `config/examples/customers_mapping.yaml`

### Scenario: clean migration
- Target file: `sample_data/customers/target_customers_clean.csv`
- Demonstrates: a correctly migrated target with renamed columns.
- Expected high-level result: no missing records, no unexpected records, no duplicate keys, and no mapped value mismatches.

### Scenario: missing records
- Target file: `sample_data/customers/target_customers_missing_records.csv`
- Demonstrates: source records absent from target.
- Expected high-level result: missing record findings for omitted customer IDs.

### Scenario: extra records
- Target file: `sample_data/customers/target_customers_extra_records.csv`
- Demonstrates: unexpected records that appear only in target.
- Expected high-level result: unexpected record findings for extra customer IDs.

### Scenario: value mismatches
- Target file: `sample_data/customers/target_customers_value_mismatches.csv`
- Demonstrates: mismatched email, status, phone, created date, and balance.
- Expected high-level result: mapped value mismatch findings for the changed fields.

### Scenario: duplicate keys
- Target file: `sample_data/customers/target_customers_duplicate_keys.csv`
- Demonstrates: duplicated `customer_id` in target.
- Expected high-level result: duplicate key findings before field-level comparisons.

## Orders

- Source file: `sample_data/orders/source_orders.csv`
- Mapping file: `config/examples/orders_mapping.yaml`

### Scenario: clean migration
- Target file: `sample_data/orders/target_orders_clean.csv`
- Demonstrates: expected source-to-target compatibility after field mapping.
- Expected high-level result: no key integrity issues, no missing/unexpected records, and no meaningful value mismatches.

### Scenario: migration issues
- Target file: `sample_data/orders/target_orders_migration_issues.csv`
- Demonstrates:
  - one missing order
  - one unexpected target order
  - one amount difference within 0.01 tolerance
  - one true amount mismatch
  - one status casing difference
  - one date formatting difference
- Expected high-level result: missing/unexpected record findings and one true amount mismatch; tolerance and normalization rules should reduce false positives.

## CRM migration (Salesforce -> Dynamics)

- Source file: `sample_data/crm_migration/source_contacts_salesforce.csv`
- Mapping file: `config/examples/crm_contacts_mapping.yaml`
- Reconciliation key: `source.salesforce_contact_id -> target.legacy_salesforce_id`

### Scenario: clean migration
- Target file: `sample_data/crm_migration/target_contacts_dynamics_clean.csv`
- Demonstrates: correct migration into Dynamics-style schema with renamed key and fields.
- Expected high-level result: no missing/unexpected records, no key-level defects, and no mapped field mismatches.

### Scenario: migration issues
- Target file: `sample_data/crm_migration/target_contacts_dynamics_issues.csv`
- Demonstrates:
  - missing migrated contact
  - unexpected target contact
  - email mismatch
  - phone mismatch
  - status/statecode mismatch
  - date formatting difference
  - owner mismatch
- Expected high-level result: deterministic checks should flag key and true value issues while allowing date normalization when configured.
