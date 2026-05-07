# Example `agent_trace.json` excerpt

Example only (illustrative):

```json
{
  "plan": {
    "status": "ready",
    "key_mode": "inferred_same_name",
    "assumptions": ["Using inferred key 'customer_id' present in both inputs."],
    "warnings": []
  },
  "deterministic_run": {
    "executed": true,
    "reconciliation_trace_path": "outputs/run/reconciliation_trace.json"
  },
  "final_status": "completed"
}
```

Use the full generated trace for actual run decisions.
