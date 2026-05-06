# Mapping File Guide

Mapping YAML files define source-to-target alignment and planned comparator intent.

## Structure

A mapping file contains:

- `entity`: logical name of the business dataset being reconciled.
- `source_key`: key column in the source dataset.
- `target_key`: key column in the target dataset.
- `field_mappings`: list of planned field-level mappings.

Each `field_mappings[]` item contains:

- `source`: source column name.
- `target`: target column name.
- `comparator`: planned comparator type (`string`, `number`, `date`, `datetime`).
- `normalize` (optional): planned normalization settings for a future comparator run.
- `tolerance` (optional): planned numeric tolerance for a future comparator run.

## Example

```yaml
entity: crm_contacts
source_key: salesforce_contact_id
target_key: legacy_salesforce_id
field_mappings:
  - source: email
    target: emailaddress1
    comparator: string
    normalize:
      trim: true
      case_sensitive: false
```

## How mapping is used in Milestone 3

In Milestone 3, mapping config is used for:

1. **Key resolution**: deterministic record matching uses `source_key` and `target_key`.
2. **Validation**: checks confirm key and mapped columns exist in the loaded datasets and comparator names are allowed.
3. **Trace/report metadata**: mapping summary is included in reconciliation artifacts.

## What is not yet implemented

Milestone 3 does **not** execute mapped field value comparison.

Specifically:

- comparator execution is not implemented yet
- normalize/tolerance settings are parsed and validated, but not executed yet
- field-level comparison starts in Milestone 4

Examples live under `config/examples/`.
