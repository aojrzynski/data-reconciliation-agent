# Adding a New Comparator

This walkthrough shows how to add a comparator while keeping reconciliation deterministic.

## 1) Where comparator logic lives

Comparator behavior belongs in:
- `src/data_reconciliation_agent/comparators.py`

Keep functions explicit and deterministic. Avoid hidden state and probabilistic behavior.

## 2) Add comparator implementation

Typical steps:
1. Add a comparator function with a clear name.
2. Return a deterministic match/mismatch result with reason details.
3. Register the comparator in the comparator selection/lookup path.

Use direct logic, not abstraction-heavy wrappers.

## 3) Reference comparator in mapping config

Mapping YAML in `config/examples/*.yaml` should reference comparator names for mapped fields.

After adding a new comparator, update or add mapping examples that exercise it.

## 4) Add tests

Minimum expected test coverage:
- unit tests in `tests/test_comparators.py` for normal and edge cases,
- reconciliation-level test proving mismatch output behavior,
- optional agent-mode scenario test if planner/mapping behavior is affected.

Test both positive matches and expected mismatches.

## 5) Add or update fixture data

If comparator needs scenario coverage:
1. Add representative source/target rows in `sample_data/`.
2. Add or update mapping in `config/examples/`.
3. Verify expected exception artifacts (especially `value_mismatches.csv`).

Keep fixture size small and inspectable.

## 6) Update docs

Update relevant docs so users can discover the comparator:
- `docs/mapping_file_guide.md`
- `docs/how_it_works.md` (if behavior changes)
- `README.md` comparator summary bullets

## 7) What not to do

Do not let an LLM decide whether values match.

Comparator decisions must stay deterministic and test-backed. The optional LLM summary layer is readability-only and non-authoritative.
