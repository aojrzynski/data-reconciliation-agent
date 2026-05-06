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


def test_key_inference_crm_does_not_infer_different_names() -> None:
    out = ROOT / "outputs" / "tmp_crm_blocked"
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        target_path=str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        output_dir=str(out),
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


def test_agent_trace_includes_planned_steps_and_authoritative_language(tmp_path: Path) -> None:
    result = run_agent_reconciliation(
        source_path=str(ROOT / "sample_data/customers/source_customers.csv"),
        target_path=str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        output_dir=str(tmp_path),
    )
    payload = json.loads((tmp_path / "agent_trace.json").read_text(encoding="utf-8"))
    assert payload["plan"]["planned_steps"]
    report = (tmp_path / "agent_report.md").read_text(encoding="utf-8")
    assert "did not decide whether values matched" in report
