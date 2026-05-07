# Mapping File Guide

Mapping YAML files define source-to-target alignment and deterministic comparator behavior.

## Structure

Top-level fields:
- `entity`
- `source_key`
- `target_key`
- `field_mappings`

Each `field_mappings[]` item:
- `source`
- `target`
- `comparator`: `string`, `number`, `date`, or `datetime`
- `normalize` (optional, string only):
  - `trim` (default `true`)
  - `case_sensitive` (default `true`)
- `tolerance` (optional, number only)

## Runtime behavior

- Mapping resolves source/target key names.
- Mapping is validated against real columns.
- Field comparators execute **only for records matched by key**.
- Missing and unexpected records are handled separately by record-level checks.

## Null handling

For all comparators:
- pandas null values (`NaN`, `NaT`) and blank strings are treated as null.
- null vs null = match (`both_null`)
- null vs non-null = mismatch (`one_null`)

## Comparator notes

- `string`: optional trim/case normalization before exact comparison.
- `number`: numeric parse required; optional tolerance (`abs(diff) <= tolerance`).
- `date`: parse and compare date component only.
- `datetime`: parse and compare full normalized UTC datetime.

Examples live under `config/examples/`.
