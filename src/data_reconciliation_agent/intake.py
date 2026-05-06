"""File intake helpers for deterministic reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class LoadedDataset:
    path: str
    dataframe: pd.DataFrame
    file_type: str
    row_count: int
    column_names: list[str]


def validate_path_exists(path: str) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")
    if not file_path.is_file():
        raise ValueError(f"Input path is not a file: {path}")
    return file_path


def detect_file_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".csv":
        return "csv"
    if ext in {".xlsx", ".xlsm"}:
        return "xlsx"
    raise ValueError(
        f"Unsupported file type for '{path}'. Supported extensions: .csv, .xlsx, .xlsm"
    )


def load_dataset(path: str) -> LoadedDataset:
    file_path = validate_path_exists(path)
    file_type = detect_file_type(str(file_path))

    if file_type == "csv":
        dataframe = pd.read_csv(file_path)
    elif file_type == "xlsx":
        dataframe = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    return LoadedDataset(
        path=str(file_path),
        dataframe=dataframe,
        file_type=file_type,
        row_count=len(dataframe),
        column_names=[str(c) for c in dataframe.columns.tolist()],
    )
