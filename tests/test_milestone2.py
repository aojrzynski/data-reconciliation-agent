from pathlib import Path
import json

import pandas as pd
import pytest

from data_reconciliation_agent.intake import load_dataset
from data_reconciliation_agent.reconciliation_checks import (
    duplicate_keys,
    key_exists,
    missing_keys,
    null_keys,
    unexpected_keys,
)
from data_reconciliation_agent.reconciliation_engine import run_deterministic_reconciliation
from data_reconciliation_agent.schema_summary import build_schema_summary

ROOT = Path(__file__).resolve().parents[1]


def test_csv_fixture_loads() -> None:
    loaded = load_dataset(str(ROOT / "sample_data/customers/source_customers.csv"))
    assert loaded.file_type == "csv"
    assert loaded.row_count > 0


def test_unsupported_extension_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_dataset(str(ROOT / "README.md"))




def test_xlsx_load_with_tmp_file(tmp_path: Path) -> None:
    dataframe = pd.DataFrame({"id": ["A", "B"], "amount": [1, 2]})
    xlsx_path = tmp_path / "sample.xlsx"
    dataframe.to_excel(xlsx_path, index=False)

    loaded = load_dataset(str(xlsx_path))
    assert loaded.file_type == "xlsx"
    assert loaded.row_count == 2
    assert loaded.column_names == ["id", "amount"]


def test_schema_summary_sets() -> None:
    source = pd.DataFrame({"id": [1], "a": [2], "c": [3]})
    target = pd.DataFrame({"id": [1], "b": [2], "c": [3]})
    summary = build_schema_summary(source, target)
    assert summary.source_only_columns == ["a"]
    assert summary.target_only_columns == ["b"]
    assert summary.common_columns == ["c", "id"]


def test_key_checks() -> None:
    df = pd.DataFrame({"id": ["A", "A", None, ""], "value": [1, 2, 3, 4]})
    assert key_exists(df, "id")
    assert not key_exists(df, "missing")
    assert len(null_keys(df, "id")) == 2
    assert len(duplicate_keys(df, "id")) == 2


def test_record_comparisons_customers_and_orders() -> None:
    c_source = pd.read_csv(ROOT / "sample_data/customers/source_customers.csv")
    c_clean = pd.read_csv(ROOT / "sample_data/customers/target_customers_clean.csv")
    c_missing = pd.read_csv(ROOT / "sample_data/customers/target_customers_missing_records.csv")
    c_extra = pd.read_csv(ROOT / "sample_data/customers/target_customers_extra_records.csv")
    c_dup = pd.read_csv(ROOT / "sample_data/customers/target_customers_duplicate_keys.csv")

    assert missing_keys(c_source, c_clean, "customer_id").empty
    assert unexpected_keys(c_source, c_clean, "customer_id").empty
    assert duplicate_keys(c_clean, "customer_id").empty

    assert set(missing_keys(c_source, c_missing, "customer_id")["customer_id"]) == {"CUST-1003", "CUST-1009"}
    assert set(unexpected_keys(c_source, c_extra, "customer_id")["customer_id"]) == {"CUST-2013", "CUST-2014"}
    assert set(duplicate_keys(c_dup, "customer_id")["customer_id"]) == {"CUST-1006"}

    o_source = pd.read_csv(ROOT / "sample_data/orders/source_orders.csv")
    o_issues = pd.read_csv(ROOT / "sample_data/orders/target_orders_migration_issues.csv")
    assert set(missing_keys(o_source, o_issues, "order_id")["order_id"]) == {"ORD-9012"}
    assert set(unexpected_keys(o_source, o_issues, "order_id")["order_id"]) == {"ORD-9999"}


def test_artifacts_written(tmp_path: Path) -> None:
    result = run_deterministic_reconciliation(
        str(ROOT / "sample_data/customers/source_customers.csv"),
        str(ROOT / "sample_data/customers/target_customers_missing_records.csv"),
        "customer_id",
        str(tmp_path),
    )
    trace_path = Path(result.trace_path)
    assert trace_path.exists()
    assert Path(result.report_path).exists()
    assert (tmp_path / "missing_in_target.csv").exists()

    trace = json.loads(trace_path.read_text())
    assert "output_files" in trace
    assert trace["output_files"]["trace"] == "reconciliation_trace.json"
    assert trace["output_files"]["report"] == "reconciliation_report.md"
    assert "exceptions_written" in trace["output_files"]
    assert "exceptions_skipped" in trace["output_files"]
    assert "duplicate_key_row_count_source" in trace["key_checks"]
    assert "duplicate_key_row_count_target" in trace["key_checks"]

    run_deterministic_reconciliation(
        str(ROOT / "sample_data/customers/source_customers.csv"),
        str(ROOT / "sample_data/customers/target_customers_extra_records.csv"),
        "customer_id",
        str(tmp_path / "extra"),
    )
    assert (tmp_path / "extra" / "unexpected_in_target.csv").exists()

    run_deterministic_reconciliation(
        str(ROOT / "sample_data/customers/source_customers.csv"),
        str(ROOT / "sample_data/customers/target_customers_duplicate_keys.csv"),
        "customer_id",
        str(tmp_path / "dup"),
    )
    assert (tmp_path / "dup" / "duplicate_keys_target.csv").exists()


def test_engine_missing_key_produces_blocking_error_and_artifacts(tmp_path: Path) -> None:
    result = run_deterministic_reconciliation(
        str(ROOT / "sample_data/customers/source_customers.csv"),
        str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "not_a_real_key",
        str(tmp_path / "missing_key"),
    )
    assert result.blocking_errors
    assert result.matched_key_count == 0
    assert Path(result.trace_path).exists()
    assert Path(result.report_path).exists()

    trace = json.loads(Path(result.trace_path).read_text())
    assert trace["blocking_errors"]
    assert any("not_a_real_key" in m for m in trace["blocking_errors"])
    assert trace["record_comparison"]["matched_key_count"] == 0
