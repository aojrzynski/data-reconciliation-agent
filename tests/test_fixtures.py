from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]

SCENARIOS = {
    "customers": {
        "source": ROOT / "sample_data/customers/source_customers.csv",
        "targets": [
            ROOT / "sample_data/customers/target_customers_clean.csv",
            ROOT / "sample_data/customers/target_customers_missing_records.csv",
            ROOT / "sample_data/customers/target_customers_extra_records.csv",
            ROOT / "sample_data/customers/target_customers_value_mismatches.csv",
            ROOT / "sample_data/customers/target_customers_duplicate_keys.csv",
        ],
        "mapping": ROOT / "config/examples/customers_mapping.yaml",
    },
    "orders": {
        "source": ROOT / "sample_data/orders/source_orders.csv",
        "targets": [
            ROOT / "sample_data/orders/target_orders_clean.csv",
            ROOT / "sample_data/orders/target_orders_migration_issues.csv",
        ],
        "mapping": ROOT / "config/examples/orders_mapping.yaml",
    },
    "crm_contacts": {
        "source": ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv",
        "targets": [
            ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv",
            ROOT / "sample_data/crm_migration/target_contacts_dynamics_issues.csv",
        ],
        "mapping": ROOT / "config/examples/crm_contacts_mapping.yaml",
    },
}


def test_fixture_files_exist() -> None:
    for scenario in SCENARIOS.values():
        assert scenario["source"].exists()
        assert scenario["mapping"].exists()
        for target in scenario["targets"]:
            assert target.exists()


def test_csv_files_are_readable_and_non_empty() -> None:
    for scenario in SCENARIOS.values():
        source = pd.read_csv(scenario["source"])
        assert not source.empty

        for target_file in scenario["targets"]:
            target = pd.read_csv(target_file)
            assert not target.empty


def test_mapping_files_contain_required_sections() -> None:
    for scenario in SCENARIOS.values():
        text = scenario["mapping"].read_text()
        assert "source_key:" in text
        assert "target_key:" in text
        assert "field_mappings:" in text


def test_mapping_fields_match_fixture_columns() -> None:
    for scenario in SCENARIOS.values():
        mapping = yaml.safe_load(scenario["mapping"].read_text())
        source_cols = set(pd.read_csv(scenario["source"]).columns)

        for target_file in scenario["targets"]:
            target_cols = set(pd.read_csv(target_file).columns)

            assert mapping["source_key"] in source_cols
            assert mapping["target_key"] in target_cols

            for field_mapping in mapping["field_mappings"]:
                assert field_mapping["source"] in source_cols
                assert field_mapping["target"] in target_cols
