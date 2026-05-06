# How It Works

## End-to-end execution

1. **Load inputs**
   - source and target datasets are loaded from CSV/XLSX.
2. **Resolve key/mapping**
   - deterministic mode: user-provided `--key` or `--mapping` is binding.
   - agent mode: planner resolves mapping/key assumptions within bounded rules.
3. **Run record checks**
   - key existence, null keys, duplicate keys, missing records, unexpected records.
4. **Run mapped value comparison**
   - runs only when mapping config is present and key joins are safe.
5. **Write exception CSVs**
   - missing/unexpected/duplicate/null key artifacts and value mismatches when present.
6. **Write deterministic artifacts**
   - `reconciliation_trace.json` and `reconciliation_report.md`.
7. **(Agent mode only) write orchestration artifacts**
   - `agent_trace.json` and `agent_report.md` describing plan, assumptions, and tool execution.

## Design rule

The deterministic engine remains authoritative. Agent mode is an orchestrator, not a judge.
