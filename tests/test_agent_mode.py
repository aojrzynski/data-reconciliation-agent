import json
from pathlib import Path

from data_reconciliation_agent.agent_runner import run_agent_reconciliation
from data_reconciliation_agent.intake import load_dataset
from data_reconciliation_agent.key_inference import infer_key_candidates

ROOT = Path(__file__).resolve().parents[1]


def test_key_inference_customers_high_confidence() -> None:
    source = load_dataset(str(ROOT / "sample_data/customers/source_customers.csv")).dataframe
    target = load_dataset(str(ROOT / "sample_data/customers/target_customers_clean.csv")).dataframe
    candidates = infer_key_candidates(source, target)
    assert candidates[0].source_key == "customer_id"
    assert candidates[0].confidence == "high"


def test_key_inference_orders_high_confidence() -> None:
    source = load_dataset(str(ROOT / "sample_data/orders/source_orders.csv")).dataframe
    target = load_dataset(str(ROOT / "sample_data/orders/target_orders_clean.csv")).dataframe
    candidates = infer_key_candidates(source, target)
    assert candidates[0].source_key == "order_id"
    assert candidates[0].confidence == "high"


def test_key_inference_crm_does_not_infer_different_names(tmp_path: Path) -> None:
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        target_path=str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        output_dir=str(tmp_path),
    )
    assert result.status == "blocked"


def test_agent_explicit_key_runs(tmp_path: Path) -> None:
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/customers/source_customers.csv"),
        target_path=str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        output_dir=str(tmp_path),
        key="customer_id",
    )
    assert result.status == "completed"
    assert (tmp_path / "agent_trace.json").exists()
    assert (tmp_path / "agent_report.md").exists()


def test_agent_mapping_runs(tmp_path: Path) -> None:
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        target_path=str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_issues.csv"),
        output_dir=str(tmp_path),
        mapping_path=str(ROOT / "config/examples/crm_contacts_mapping.yaml"),
    )
    assert result.status == "completed"
    assert result.deterministic_result.value_comparison_enabled is True
    assert result.plan.source_key == "salesforce_contact_id"
    assert result.plan.target_key == "legacy_salesforce_id"


def test_agent_orders_infers_order_id_and_runs(tmp_path: Path) -> None:
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/orders/source_orders.csv"),
        target_path=str(ROOT / "sample_data/orders/target_orders_clean.csv"),
        output_dir=str(tmp_path),
    )
    assert result.status == "completed"
    assert result.plan.source_key == "order_id"


def test_ambiguous_high_candidates_block(tmp_path: Path) -> None:
    source = tmp_path / "source.csv"
    target = tmp_path / "target.csv"
    source.write_text("customer_id,order_id\n10,1\n20,2\n30,3\n", encoding="utf-8")
    target.write_text("order_id,customer_id\n1,10\n2,20\n3,30\n", encoding="utf-8")
    result = run_agent_reconciliation(str(source), str(target), str(tmp_path / "out"))
    assert result.status == "blocked"


def test_agent_invalid_mapping_path_writes_blocked_artifacts(tmp_path: Path) -> None:
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/customers/source_customers.csv"),
        target_path=str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        output_dir=str(tmp_path),
        mapping_path=str(tmp_path / "missing_mapping.yaml"),
    )
    assert result.status == "blocked"
    assert (tmp_path / "agent_trace.json").exists()
    assert (tmp_path / "agent_report.md").exists()


def test_agent_trace_includes_planned_steps_and_authoritative_language(tmp_path: Path) -> None:
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/customers/source_customers.csv"),
        target_path=str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        output_dir=str(tmp_path),
    )
    payload = json.loads((tmp_path / "agent_trace.json").read_text(encoding="utf-8"))
    assert payload["plan"]["planned_steps"]
    assert "warnings" in payload
    assert "blocking_errors" in payload
    assert "deterministic_run" in payload
    report = (tmp_path / "agent_report.md").read_text(encoding="utf-8")
    assert "did not decide whether values matched" in report
    assert "Deterministic reconciliation outputs remain authoritative" in report
    assert "Report path:" in report
