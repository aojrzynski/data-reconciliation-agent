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


## Milestone 3 note
Mapping config now supports `entity`, `source_key`, `target_key`, and `field_mappings` validation for deterministic key resolution. Mapped field value comparison/comparator execution starts in Milestone 4.
