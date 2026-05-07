# Project Scope

## In scope (v1)

- Deterministic source-to-target reconciliation for CSV/XLSX datasets.
- Key-based checks: missing/unexpected records, null keys, duplicate keys.
- Mapping-driven field comparison with deterministic comparators.
- Bounded agent mode for planning/orchestration.
- Trace/report/exception artifacts for auditability.
- Optional non-authoritative LLM polish from deterministic metadata.

## Out of scope (v1)

- Fuzzy matching and entity resolution.
- Automatic data correction.
- Autonomous open-ended agents.
- Database connectors.
- Web UI.
- Full migration platform workflow orchestration.

## v1 assumptions

- Users can provide source/target files locally.
- Users can provide explicit key or mapping when inference is unsafe.
- Deterministic checks are the decision authority.
- Agent mode must block instead of guessing when uncertain.

## Authority model

- Deterministic artifacts are canonical evidence.
- Agent artifacts explain orchestration decisions.
- LLM summaries are readability-only and non-authoritative.

## Local-first posture

- Runs from CLI in local environments.
- Core value does not depend on external services.
- Optional OpenAI polish is additive and can fail closed to deterministic fallback.

## Privacy and data handling expectations

- Deterministic reconciliation runs locally.
- Optional LLM summary is based on deterministic trace metadata.
- Raw datasets and exception row contents are not sent for summary generation.
- Teams should still review environment, logging, and policy requirements before using external providers.
