# Mapping File Guide

Mapping YAML files define source-to-target field relationships and comparator intent.

Current example mapping structure uses:

- entity
- source_key
- target_key
- field_mappings[]
  - source
  - target
  - comparator
  - optional normalize
  - optional tolerance

Planned deterministic comparators include:

- string
- number
- date
- datetime

Examples live under `config/examples/`.
