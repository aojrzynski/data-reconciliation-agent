# Architecture

## Design intent

This project is designed for source-to-target reconciliation where deterministic evidence is the authority. The architecture is intentionally simple:

- local-first execution,
- CLI-first operation,
- narrow, testable modules,
- bounded orchestration in agent mode,
- optional LLM polish only after deterministic artifacts exist.

The design avoids heavyweight frameworks so behavior stays inspectable and predictable.

## Layered view

### 1) Input and intake layer

Responsibilities:
- Parse CLI arguments.
- Validate mode-level requirements.
- Load source and target files (CSV/XLSX).
- Route deterministic vs agent execution paths.

Primary modules:
- `src/data_reconciliation_agent/cli.py`
- `src/data_reconciliation_agent/io_utils.py`

### 2) Mapping and config layer

Responsibilities:
- Parse mapping YAML.
- Validate schema assumptions (source key, target key, mapped fields).
- Resolve comparator names per mapped field.

Primary modules:
- `src/data_reconciliation_agent/mapping.py`
- `config/examples/*.yaml`

### 3) Deterministic reconciliation layer

Responsibilities:
- Perform canonical checks on key integrity and record presence.
- Compute missing/unexpected records.
- Gate value comparisons to matched keys only.
- Produce deterministic trace/report and exception artifacts.

Primary modules:
- `src/data_reconciliation_agent/reconciliation_engine.py`
- `src/data_reconciliation_agent/reporting.py`

### 4) Comparator layer

Responsibilities:
- Execute deterministic field-level equality/tolerance behavior.
- Support string/number/date/datetime comparison rules.
- Return explicit mismatch reasons.

Primary modules:
- `src/data_reconciliation_agent/comparators.py`

### 5) Agent orchestration layer

Responsibilities:
- Build explicit plan in bounded rules.
- Resolve key/mapping strategy and assumptions.
- Infer safe same-name key only when criteria are met.
- Block when assumptions are unsafe or ambiguous.
- Call deterministic tools only when plan is runnable.

Primary modules:
- `src/data_reconciliation_agent/planner.py`
- `src/data_reconciliation_agent/tools.py`
- `src/data_reconciliation_agent/agent_runner.py`

### 6) Reporting and artifact layer

Responsibilities:
- Write deterministic evidence artifacts.
- Write agent orchestration artifacts.
- Keep outputs auditable and easy to inspect.

Deterministic artifacts:
- `reconciliation_trace.json`
- `reconciliation_report.md`
- exception CSV files

Agent artifacts:
- `agent_trace.json`
- `agent_report.md`

### 7) Optional LLM polish layer

Responsibilities:
- Generate non-authoritative readability summary from deterministic trace metadata.
- Use deterministic fallback by default/offline.
- Optionally use OpenAI if configured.

Primary module:
- `src/data_reconciliation_agent/llm_summary.py`

## Runtime flows

### Deterministic mode

1. CLI receives explicit `--key` or `--mapping`.
2. Inputs are loaded.
3. Mapping is parsed if provided.
4. Deterministic reconciliation runs.
5. Deterministic artifacts are written.
6. Optional `--llm-summary` writes `llm_summary.md`.

### Agent mode

1. CLI enters agent path.
2. Planner inspects inputs and user-provided hints.
3. Planner resolves key/mapping approach or blocks safely.
4. If runnable, tools invoke deterministic reconciliation.
5. Agent artifacts are written with assumptions/warnings/blocking reasons.
6. Optional `--llm-summary` may run only if deterministic reconciliation executed.

### Optional LLM summary path

1. Read deterministic trace metadata.
2. Build constrained summary prompt with authority warning.
3. Use provider:
   - `deterministic_fallback` by default or on provider failure,
   - `openai` when optional dependency and API key are available.
4. Write `llm_summary.md` with provider metadata.

## Authority boundaries

- Deterministic outputs are canonical reconciliation evidence.
- Agent outputs explain orchestration decisions and assumptions.
- LLM summaries are non-authoritative readability helpers.

If wording differs between artifacts, rely on deterministic trace/report/exception CSVs.

## Why no agent framework for v1

v1 uses custom bounded orchestration instead of an agent framework because:

- the planning surface is narrow,
- deterministic checks already define truth,
- explicit control flow is easier to test,
- fewer dependencies improves local reliability,
- this keeps the "agent" role focused on coordination, not judgment.
