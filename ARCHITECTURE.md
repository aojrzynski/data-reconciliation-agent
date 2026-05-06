# Architecture

This project separates deterministic reconciliation from agent orchestration on purpose.

## 1. CLI layer

The CLI is the main user interface. It accepts source/target paths, key, optional mapping, execution mode, and output settings. It should stay simple and transparent.

## 2. Intake layer

The intake layer validates run inputs and resolves assumptions:

- file format and existence
- dataset loading boundaries
- key selection (explicit or inferred)
- mapping availability

The intake layer should fail clearly when assumptions are invalid.

## 3. Deterministic reconciliation engine

The reconciliation engine owns the actual source-to-target validation logic. It runs checks in a predictable sequence and emits machine-readable outcomes.

This is the authority for whether data is preserved.

## 4. Comparators

Comparators are focused deterministic units for value-level checks:

- string compare
- numeric compare with tolerance
- date compare
- null handling behavior

Comparators should be explicit and easy to test.

## 5. Mapping config

Mapping configuration defines how source fields correspond to target fields and what comparison rules apply. This keeps reconciliation logic reusable across entities and migrations.

## 6. Agent runner

Agent mode coordinates deterministic tools. It should:

- interpret intake context
- select appropriate deterministic steps
- run bounded investigations
- summarize outcomes and assumptions

It should not invent reconciliation outcomes.

## 7. Reporting and trace layer

The reporting layer emits readable markdown for humans. The trace layer emits structured JSON for auditability. Exception writer outputs concrete mismatch records for investigation.

## 8. Optional LLM polish

An optional LLM layer may improve report readability. It is non-authoritative and must not alter deterministic outcomes.

## Why the agent does not directly decide whether data matches

LLM output can be useful for communication, but it is not a reliable authority for exact data equality or mapping correctness. Deterministic checks provide consistent, testable, and repeatable judgments. The agent layer exists to orchestrate those checks, not replace them.


## Milestone 5 Agent Mode

Agent mode is now implemented as a bounded orchestration layer. It resolves key/mapping assumptions, writes `agent_trace.json` and `agent_report.md`, and then calls the deterministic engine. Deterministic outputs remain authoritative.
