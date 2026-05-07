# Interpreting Outputs

This guide explains how to read each artifact and how to keep authority boundaries clear.

## 1) Start with deterministic artifacts

Deterministic artifacts are canonical:
- `reconciliation_trace.json`
- `reconciliation_report.md`
- exception CSV files

Use these first for conclusions.

## 2) Reading `reconciliation_trace.json`

Typical sections to review:
- input context: source/target paths, mode, mapping/key settings
- key integrity summaries: nulls, duplicates, key column status
- record-level counts: missing in target, unexpected in target, matched keys
- value comparison summary: mapped fields checked, mismatch counts
- artifact paths and metadata

What it tells you:
- exactly what checks ran,
- exactly what counts were found,
- where to find row-level evidence.

## 3) Reading `reconciliation_report.md`

Use the report for a concise run narrative:
- high-level pass/fail posture by check category,
- key counts and mismatch summaries,
- links/paths to generated artifacts.

It is human-oriented but still deterministic in content.

## 4) Exception CSV creation rules

Exception files are created only for categories with rows.

If you do not see a specific file, that usually means either:
- no issues were found in that category, or
- that check did not run (for example value comparisons without mapping).

## 5) Reading `value_mismatches.csv`

`value_mismatches.csv` is row-level field evidence for mapped comparisons.

Read it as:
- which matched record key had a mismatch,
- which mapped field failed,
- source value vs target value,
- comparator context/reason when available.

Interpretation reminder: this file is only populated from matched-key joins; unmatched rows are handled by missing/unexpected artifacts.

## 6) Reading `agent_trace.json`

`agent_trace.json` explains orchestration decisions, including:
- chosen key/mapping strategy,
- assumptions and warnings,
- candidate keys considered during inference,
- blocking reasons when execution is halted,
- deterministic execution status and referenced artifact paths.

Use it to audit *how the plan was made*, not to replace deterministic evidence.

## 7) Reading `agent_report.md`

`agent_report.md` is the human-readable version of agent orchestration state:
- final status,
- plan status,
- assumptions/warnings/blockers,
- deterministic run summary when executed.

It should help teammates understand why agent mode proceeded or stopped.

## 8) Interpreting `llm_summary.md` safely

`llm_summary.md` is optional and non-authoritative.

Safe usage:
- treat it as a readability layer,
- verify claims against deterministic artifacts,
- never use it as sole sign-off evidence.

Provider metadata indicates generation path:
- `deterministic_fallback`: local deterministic summary path,
- `openai`: optional external polish path.

Either way, authoritative truth remains deterministic trace/report/exception CSVs.

## 9) Fast triage order (recommended)

1. Open `reconciliation_trace.json` for counts and execution details.
2. Review exception CSVs for row-level evidence.
3. Read `reconciliation_report.md` for concise narrative.
4. If agent mode was used, read `agent_trace.json` and `agent_report.md` for orchestration context.
5. If present, read `llm_summary.md` last as a communication aid.
