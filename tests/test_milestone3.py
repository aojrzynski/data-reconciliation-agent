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


def test_crm_mapping_reconciliation_clean(tmp_path: Path) -> None:
    result = run_deterministic_reconciliation(
        source_path=str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        target_path=str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        output_dir=str(tmp_path),
        mapping_path=str(ROOT / "config/examples/crm_contacts_mapping.yaml"),
    )
    assert result.matched_key_count == 10
    assert result.missing_in_target_count == 0
    assert result.unexpected_in_target_count == 0


def test_crm_mapping_reconciliation_issues(tmp_path: Path) -> None:
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

    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert trace["key_mode"] == "mapping_config"
    assert trace["source_key"] == "salesforce_contact_id"
    assert trace["target_key"] == "legacy_salesforce_id"
    assert trace["mapping_config"]["entity"] == "crm_contacts"
    assert "exceptions_skipped_empty" in trace["output_files"]
