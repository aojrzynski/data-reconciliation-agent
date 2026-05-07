# Example `agent_trace.json` excerpt

Example only (illustrative):

```json
{
  "plan": {
    "status": "runnable",
    "key_mode": "inferred_same_name_key",
    "assumptions": ["Using inferred key 'customer_id' present in both inputs."],
    "warnings": []
  },
  "deterministic_run": {
    "executed": true,
    "trace_path": "outputs/run/reconciliation_trace.json"
  },
  "final_status": "completed"
}
```

Use the full generated trace for actual run decisions.
