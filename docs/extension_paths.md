# Extension Paths

This guide explains safe ways to extend the project without breaking the authority model.

## First rule: keep deterministic logic authoritative

Extensions should preserve this boundary:
- deterministic engine decides reconciliation outcomes,
- agent mode coordinates,
- optional LLM layer summarizes only.

## Add a new comparator

1. Implement comparator behavior in `src/data_reconciliation_agent/comparators.py`.
2. Register it in comparator lookup logic.
3. Add tests in `tests/test_comparators.py` and scenario-level tests if needed.
4. Reference it from mapping YAML where appropriate.
5. Document behavior and edge cases.

## Add a new fixture scenario

1. Add source/target sample files under `sample_data/`.
2. Add or update mapping file under `config/examples/` if needed.
3. Add focused tests for expected counts and artifacts.
4. Document scenario in `docs/sample_scenarios.md` and/or `docs/example_commands.md`.

## Add a new mapping file

1. Copy an existing mapping in `config/examples/`.
2. Update `source_key`, `target_key`, and field mappings.
3. Validate with deterministic run.
4. Add tests for mapping parsing/validation and scenario outcome.

## Add a new exception artifact

1. Decide deterministic trigger condition.
2. Generate artifact from deterministic engine/reporting layer.
3. Include artifact path/counts in trace metadata.
4. Add tests for both created and skipped cases.
5. Update `docs/interpreting_outputs.md` and README artifact section.

## Improve key inference

1. Keep logic in planner/agent layer only.
2. Prefer explicit, explainable heuristics.
3. Block when uncertain rather than guessing.
4. Record assumptions and warnings in agent trace/report.
5. Add tests for both successful inference and safe blocking.

## Improve LLM summary prompt safely

1. Edit `src/data_reconciliation_agent/llm_summary.py` prompt text only.
2. Preserve explicit statement that deterministic outputs are authoritative.
3. Keep restriction: no markdown links and no invented evidence.
4. Ensure summary input remains deterministic trace metadata, not raw rows.
5. Run `tests/test_llm_summary.py`.

## Add database input later (without changing core engine)

Suggested path:
1. Build adapters that materialize source/target extracts into DataFrame-equivalent inputs.
2. Keep reconciliation engine interfaces stable.
3. Keep deterministic checks unchanged.
4. Reuse existing artifact/reporting pipeline.
5. Add integration tests that prove parity with CSV/XLSX behavior.

This keeps storage concerns at intake boundaries and protects core deterministic behavior.
