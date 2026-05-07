"""Write row-level exception CSV evidence for deterministic reconciliation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_exception_csv(output_dir: Path, filename: str, dataframe: pd.DataFrame) -> str | None:
    """Write exception rows when present; skip empty files to keep output focused."""
    if dataframe.empty:
        return None
    output_path = output_dir / filename
    dataframe.to_csv(output_path, index=False)
    return str(output_path)
