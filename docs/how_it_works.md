# How It Works

This walkthrough explains what happens from CLI input to output artifacts.

## 1) User provides source and target

Every run starts with:
- `--source`
- `--target`
- `--mode deterministic` or `--mode agent`

Both files are loaded from local CSV/XLSX inputs.

## 2) Key and mapping resolution

### If user provides `--key`

- The key is treated as authoritative for joining source and target records.
- Deterministic checks run using that key.
- If key columns are missing/null-heavy/duplicate, those issues appear in trace and exception outputs.

### If user provides `--mapping`

- Mapping YAML defines `source_key`, `target_key`, and mapped fields.
- The mapping becomes authoritative for join behavior and value comparison scope.
- Mapped field comparators are read from mapping config.

### If agent mode is used with no key/mapping

- Planner inspects column names and safe inference rules.
- If a same-name key candidate is clearly safe, planner records assumption and continues.
- If inference is ambiguous or unsafe, planner blocks execution and explains why.

### When key inference is blocked

Typical block reasons:
- no shared key-like column names,
- multiple plausible candidates,
- confidence checks fail.

In this case agent artifacts are written, deterministic reconciliation is skipped, and the report explains what must be provided explicitly.

## 3) Deterministic reconciliation checks

Once key strategy is resolved, deterministic engine runs:
- key existence checks,
- null key checks,
- duplicate key checks,
- missing-in-target detection,
- unexpected-in-target detection.

These checks are canonical evidence.

## 4) Mapped value comparison

Mapped value comparison runs only when:
- mapping is present, and
- key-based record matching is available.

Why this gate exists: value comparison is meaningful only for matched source/target records. Comparing unmapped or unmatched rows introduces false noise.

Comparators are deterministic (string/number/date/datetime) and produce explicit mismatch rows.

## 5) Exception files

Exception CSVs are produced only when relevant issues exist.

Common artifacts:
- `missing_in_target.csv`
- `unexpected_in_target.csv`
- `duplicate_keys_source.csv`
- `duplicate_keys_target.csv`
- `null_keys_source.csv`
- `null_keys_target.csv`
- `value_mismatches.csv` (when mapping comparison finds mismatches)

If a category has no rows, that artifact is skipped.

## 6) Deterministic trace and report

Every successful deterministic execution writes:
- `reconciliation_trace.json` (machine-readable details)
- `reconciliation_report.md` (human-readable summary)

These are the primary outputs for reconciliation decisions.

## 7) Agent artifacts (agent mode)

Agent mode additionally writes:
- `agent_trace.json`
- `agent_report.md`

They capture:
- plan status,
- assumptions,
- warnings,
- blocking reasons,
- whether deterministic run executed.

## 8) Optional LLM summary

If `--llm-summary` is set, the system reads deterministic trace metadata and writes `llm_summary.md`.

Important constraints:
- summary is non-authoritative,
- raw dataset rows and exception row contents are not sent,
- provider metadata records `deterministic_fallback` or `openai`.

The LLM layer improves readability; it does not change reconciliation outcomes.
