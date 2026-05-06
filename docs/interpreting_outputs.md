# Interpreting Outputs

Deterministic mode produces inspectable artifacts:

- `reconciliation_trace.json`: machine-readable run metadata and counts.
- `reconciliation_report.md`: human-readable deterministic summary.
- Exception CSVs for concrete row-level exceptions.

## `reconciliation_trace.json`

Key sections:
- `mode`, `source_path`, `target_path`
- `key_mode`, `source_key`, `target_key`
- `mapping_config_path` and `mapping_config` (when mapping is used)
- `key_checks`
- `record_comparison`
- `value_comparison`
- `output_files`
- `checks_skipped`, `warnings`, `blocking_errors`

### `trace.value_comparison`

- `enabled`: whether mapped value comparison ran.
- `skipped_reason`: why it did not run, if skipped.
- `fields_compared`: number of configured mapped fields.
- `matched_records_compared`: number of matched keys compared at value level.
- `total_field_comparisons`: total field-level comparisons performed.
- `mismatched_value_count`: number of mismatched mapped field values.
- `mismatched_field_counts`: mismatch counts grouped by `source_field -> target_field`.
- `comparators_used`: comparator types used in the run.

Value comparison only runs for records matched by key. Missing and unexpected records are handled separately by record-level reconciliation.

## `value_mismatches.csv`

Written only when value comparison runs and mismatches exist.

Columns:
- `key`
- `source_key`
- `target_key`
- `source_field`
- `target_field`
- `comparator`
- `source_value`
- `target_value`
- `source_normalized`
- `target_normalized`
- `reason`

If no mismatches exist, this file is not created and is listed under `output_files.exceptions_skipped_empty`.

## Other exception CSV outputs

When relevant rows exist, the run writes:
- `missing_in_target.csv`
- `unexpected_in_target.csv`
- `duplicate_keys_source.csv`
- `duplicate_keys_target.csv`
- `null_keys_source.csv`
- `null_keys_target.csv`


## Milestone 5 Agent Mode

Agent mode is now implemented as a bounded orchestration layer. It resolves key/mapping assumptions, writes `agent_trace.json` and `agent_report.md`, and then calls the deterministic engine. Deterministic outputs remain authoritative.
