from pathlib import Path
import json

import pandas as pd
import pytest

from data_reconciliation_agent.mapping import load_mapping_config, validate_mapping_config
from data_reconciliation_agent.reconciliation_engine import run_deterministic_reconciliation

ROOT = Path(__file__).resolve().parents[1]


def test_mapping_configs_load() -> None:
    customers = load_mapping_config(str(ROOT / "config/examples/customers_mapping.yaml"))
    orders = load_mapping_config(str(ROOT / "config/examples/orders_mapping.yaml"))
    crm = load_mapping_config(str(ROOT / "config/examples/crm_contacts_mapping.yaml"))
    assert customers.entity == "customers"
    assert orders.entity == "orders"
    assert crm.source_key == "salesforce_contact_id"
    assert crm.target_key == "legacy_salesforce_id"


def test_mapping_config_invalid_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="dictionary"):
        load_mapping_config(str(bad))


def test_mapping_config_invalid_yaml_syntax_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad_syntax.yaml"
    bad.write_text("entity: crm_contacts\nfield_mappings: [", encoding="utf-8")
    with pytest.raises(ValueError, match="Could not parse mapping YAML"):
        load_mapping_config(str(bad))


def test_mapping_validation_missing_fields() -> None:
    crm = load_mapping_config(str(ROOT / "config/examples/crm_contacts_mapping.yaml"))
    errors = validate_mapping_config(crm, ["id"], ["id"])
    assert errors


def test_customers_clean_mapping_run_has_no_value_mismatch_file(tmp_path: Path) -> None:
    out = tmp_path / "customers_clean"
    run_deterministic_reconciliation(
        source_path=str(ROOT / "sample_data/customers/source_customers.csv"),
        target_path=str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        output_dir=str(out),
        mapping_path=str(ROOT / "config/examples/customers_mapping.yaml"),
    )
    assert not (out / "value_mismatches.csv").exists()


def test_customers_value_mismatch_fixture_writes_value_mismatches(tmp_path: Path) -> None:
    out = tmp_path / "customers_mismatch"
    run_deterministic_reconciliation(
        source_path=str(ROOT / "sample_data/customers/source_customers.csv"),
        target_path=str(ROOT / "sample_data/customers/target_customers_value_mismatches.csv"),
        output_dir=str(out),
        mapping_path=str(ROOT / "config/examples/customers_mapping.yaml"),
    )
    mismatches = pd.read_csv(out / "value_mismatches.csv")
    assert {"email", "status", "phone", "signup_date", "account_balance"}.issubset(set(mismatches["source_field"]))


def test_crm_mapping_reconciliation_issues_has_expected_value_mismatches(tmp_path: Path) -> None:
    out = tmp_path / "issues"
    result = run_deterministic_reconciliation(
        source_path=str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        target_path=str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_issues.csv"),
        output_dir=str(out),
        mapping_path=str(ROOT / "config/examples/crm_contacts_mapping.yaml"),
    )
    assert result.missing_in_target_count == 1
    assert result.unexpected_in_target_count == 1
    missing = pd.read_csv(out / "missing_in_target.csv")
    unexpected = pd.read_csv(out / "unexpected_in_target.csv")
    assert set(missing["salesforce_contact_id"]) == {"SF-007"}
    assert set(unexpected["legacy_salesforce_id"]) == {"SF-999"}

    mismatches = pd.read_csv(out / "value_mismatches.csv")
    assert ((mismatches["key"] == "SF-002") & (mismatches["source_field"] == "email")).any()
    assert ((mismatches["key"] == "SF-003") & (mismatches["source_field"] == "phone")).any()
    assert ((mismatches["key"] == "SF-004") & (mismatches["source_field"] == "contact_status")).any()
    assert ((mismatches["key"] == "SF-006") & (mismatches["source_field"] == "owner_id")).any()
    assert not ((mismatches["key"] == "SF-005") & (mismatches["source_field"] == "created_date")).any()

    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert trace["value_comparison"]["enabled"] is True


def test_orders_mapping_value_comparison_excludes_tolerated_and_normalized_matches(tmp_path: Path) -> None:
    out = tmp_path / "orders"
    result = run_deterministic_reconciliation(
        source_path=str(ROOT / "sample_data/orders/source_orders.csv"),
        target_path=str(ROOT / "sample_data/orders/target_orders_migration_issues.csv"),
        output_dir=str(out),
        mapping_path=str(ROOT / "config/examples/orders_mapping.yaml"),
    )
    assert result.missing_in_target_count == 1
    assert result.unexpected_in_target_count == 1
    mismatches = pd.read_csv(out / "value_mismatches.csv")
    assert not ((mismatches["key"] == "ORD-9006") & (mismatches["source_field"] == "amount")).any()
    assert ((mismatches["key"] == "ORD-9007") & (mismatches["source_field"] == "amount")).any()
    assert not ((mismatches["key"] == "ORD-9002") & (mismatches["source_field"] == "status")).any()
    assert not ((mismatches["key"] == "ORD-9004") & (mismatches["source_field"] == "order_date")).any()


def test_duplicate_keys_skip_value_comparison(tmp_path: Path) -> None:
    out = tmp_path / "dup"
    result = run_deterministic_reconciliation(
        source_path=str(ROOT / "sample_data/customers/source_customers.csv"),
        target_path=str(ROOT / "sample_data/customers/target_customers_duplicate_keys.csv"),
        output_dir=str(out),
        mapping_path=str(ROOT / "config/examples/customers_mapping.yaml"),
    )
    assert result.value_comparison_enabled is False
    assert (out / "duplicate_keys_target.csv").exists()
    assert not (out / "value_mismatches.csv").exists()
    trace = json.loads((out / "reconciliation_trace.json").read_text(encoding="utf-8"))
    assert "duplicate keys" in trace["value_comparison"]["skipped_reason"]
    assert any("duplicate keys" in item.lower() for item in trace["checks_skipped"])


def test_value_comparison_uses_normalized_key_lookup(tmp_path: Path) -> None:
    source_df = pd.DataFrame(
        [
            {"id": " 001 ", "name": "Alice", "balance": "10.00"},
            {"id": "002", "name": "Bob", "balance": "11.00"},
        ]
    )
    target_df = pd.DataFrame(
        [
            {"id": "001", "name_t": "alice", "balance_t": "10.00"},
            {"id": "002 ", "name_t": "Bob", "balance_t": "12.00"},
        ]
    )
    source_path = tmp_path / "source.csv"
    target_path = tmp_path / "target.csv"
    mapping_path = tmp_path / "mapping.yaml"
    source_df.to_csv(source_path, index=False)
    target_df.to_csv(target_path, index=False)
    mapping_path.write_text(
        "\n".join(
            [
                "entity: test",
                "source_key: id",
                "target_key: id",
                "field_mappings:",
                "  - source: name",
                "    target: name_t",
                "    comparator: string",
                "    normalize:",
                "      trim: true",
                "      case_sensitive: false",
                "  - source: balance",
                "    target: balance_t",
                "    comparator: number",
                "    tolerance: 0.0",
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    run_deterministic_reconciliation(
        source_path=str(source_path),
        target_path=str(target_path),
        output_dir=str(out),
        mapping_path=str(mapping_path),
    )
    mismatches = pd.read_csv(out / "value_mismatches.csv", dtype=str)
    assert ((mismatches["key"] == "002") & (mismatches["source_field"] == "balance")).any()
