# Interpreting Outputs

Milestone 2 produces deterministic, inspectable artifacts:

- `reconciliation_trace.json`: machine-readable run metadata and counts.
- `reconciliation_report.md`: human-readable deterministic summary.
- Exception CSVs for concrete row-level exceptions.

## `reconciliation_trace.json`

The trace includes:

- UTC timestamp
- mode (`deterministic`)
- source/target paths and key
- row and column summaries
- key checks (exists/null/duplicate counts)
- record comparison counts (matched/missing/unexpected)
- output files written
- warnings
- skipped steps

## `reconciliation_report.md`

The report summarizes the same deterministic results in markdown sections:

- input summary
- key summary
- row/record reconciliation summary
- column summary
- exception files written
- warnings and skipped checks

It explicitly states that mapped value comparison is not implemented in Milestone 2.

## Exception CSV outputs

When relevant rows exist, the run writes:

- `missing_in_target.csv`
- `unexpected_in_target.csv`
- `duplicate_keys_source.csv`
- `duplicate_keys_target.csv`
- `null_keys_source.csv`
- `null_keys_target.csv`

To reduce clutter, empty exception files are not created. The trace/report lists skipped exception files when no relevant rows were found.
