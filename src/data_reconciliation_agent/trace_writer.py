"""Write the machine-readable deterministic reconciliation trace artifact."""

from __future__ import annotations

import json
from pathlib import Path


def write_trace(output_dir: Path, trace_data: dict) -> str:
    """Persist canonical JSON evidence consumed by reports, agents, and summaries."""
    trace_path = output_dir / "reconciliation_trace.json"
    trace_path.write_text(json.dumps(trace_data, indent=2, sort_keys=True), encoding="utf-8")
    return str(trace_path)
