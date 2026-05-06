# Interpreting Outputs

Deterministic mode produces inspectable artifacts:

- `reconciliation_trace.json`: machine-readable run metadata and counts.
- `reconciliation_report.md`: human-readable deterministic summary.
- Exception CSVs for concrete row-level exceptions.

## `reconciliation_trace.json`

The trace includes:

- `mode`: deterministic mode marker.
- `source_path`, `target_path`: input file paths.
- `key_mode`: either `explicit_same_name_key` or `mapping_config`.
- `source_key`, `target_key`: actual key columns used for matching.
- `mapping_config_path`: mapping file used (when present).
- `mapping_config` summary (when present):
  - `entity`
  - `source_key`
  - `target_key`
  - `mapped_field_count`
  - `planned_comparators`
- row and column summaries.
- key checks (exists/null/duplicate counts).
- record comparison counts (`matched_key_count`, `missing_in_target_count`, `unexpected_in_target_count`).
- `output_files`:
  - `trace`
  - `report`
  - `exceptions_written`
  - `exceptions_skipped_empty`
- `checks_skipped` (actual skipped reconciliation checks only).
- `warnings` and `blocking_errors`.

## `reconciliation_report.md`

The report mirrors the deterministic run in sections:

- input summary (including key mode and source/target keys)
- mapping config summary (when mapping is used)
- key summary
- row/record reconciliation summary
- exception files written
- exception files not created because there were no relevant rows
- skipped checks
- warnings and blocking errors

## Exception CSV outputs

When relevant rows exist, the run writes:

- `missing_in_target.csv`
- `unexpected_in_target.csv`
- `duplicate_keys_source.csv`
- `duplicate_keys_target.csv`
- `null_keys_source.csv`
- `null_keys_target.csv`

If an exception output has no rows, the file is not created and is listed under `exceptions_skipped_empty` (not under skipped checks).

Mapped value comparison runs only when mapping config is provided and key comparison is valid.
