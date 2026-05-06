import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return subprocess.run(
        [sys.executable, "-m", "data_reconciliation_agent.cli", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_cli_help_exits_successfully() -> None:
    result = _run_cli(["--help"])
    assert result.returncode == 0
    assert "--source" in result.stdout
    assert "--target" in result.stdout


def test_cli_deterministic_clean_exits_zero(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--key", "customer_id",
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0


def test_cli_mapping_crm_clean_exits_zero(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        "--mapping", str(ROOT / "config/examples/crm_contacts_mapping.yaml"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert "Key mode: mapping_config" in result.stdout
    assert "Source key: salesforce_contact_id" in result.stdout
    assert "Target key: legacy_salesforce_id" in result.stdout


def test_cli_mapping_crm_issues_writes_exceptions(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_issues.csv"),
        "--mapping", str(ROOT / "config/examples/crm_contacts_mapping.yaml"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert (tmp_path / "missing_in_target.csv").exists()
    assert (tmp_path / "unexpected_in_target.csv").exists()
    assert (tmp_path / "value_mismatches.csv").exists()
    assert "Value comparison: ran" in result.stdout
    assert "Value mismatches:" in result.stdout


def test_cli_same_name_key_without_mapping_shows_value_comparison_skipped(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--key", "customer_id",
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert "Value comparison: skipped - no mapping config provided" in result.stdout


def test_cli_duplicate_keys_mapping_shows_duplicate_skip_reason(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_duplicate_keys.csv"),
        "--mapping", str(ROOT / "config/examples/customers_mapping.yaml"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert "Value comparison: skipped - duplicate keys present; row lookup is ambiguous" in result.stdout


def test_cli_with_neither_key_nor_mapping_exits_non_zero(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode != 0


def test_cli_both_key_and_mapping_warns_mapping_wins(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        "--mapping", str(ROOT / "config/examples/crm_contacts_mapping.yaml"),
        "--key", "customer_id",
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert "--mapping was provided" in result.stdout


def test_cli_missing_file_error_is_clean(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(tmp_path / "does_not_exist.csv"),
        "--key", "customer_id",
        "--output-dir", str(tmp_path / "out"),
    ])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Error:" in combined
    assert "Traceback" not in combined


def test_cli_nonexistent_key_exits_non_zero_and_writes_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "missing_key"
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--key", "not_a_real_key",
        "--output-dir", str(out_dir),
    ])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "could not complete record-level comparison" in combined
    assert "Traceback" not in combined
    assert (out_dir / "reconciliation_trace.json").exists()
    assert (out_dir / "reconciliation_report.md").exists()


def test_cli_invalid_mapping_exits_non_zero_without_traceback(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        "--mapping", str(tmp_path / "missing.yaml"),
        "--output-dir", str(tmp_path),
    ])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Traceback" not in combined




def test_cli_malformed_mapping_yaml_exits_non_zero_without_traceback(tmp_path: Path) -> None:
    bad = tmp_path / "bad_mapping.yaml"
    bad.write_text("entity: crm_contacts\nfield_mappings: [", encoding="utf-8")

    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        "--mapping", str(bad),
        "--output-dir", str(tmp_path / "out"),
    ])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Error:" in combined
    assert "Traceback" not in combined
def test_cli_agent_customers_exits_zero_and_writes_outputs(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "agent",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert (tmp_path / "agent_trace.json").exists()
    assert (tmp_path / "agent_report.md").exists()


def test_cli_agent_crm_without_mapping_exits_non_zero_and_writes_outputs(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "agent",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode != 0
    assert (tmp_path / "agent_trace.json").exists()
    assert (tmp_path / "agent_report.md").exists()


def test_cli_agent_crm_mapping_exits_zero(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "agent",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        "--mapping", str(ROOT / "config/examples/crm_contacts_mapping.yaml"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert "Source key: salesforce_contact_id" in result.stdout
    assert "Target key: legacy_salesforce_id" in result.stdout
    trace = (tmp_path / "reconciliation_trace.json").read_text(encoding="utf-8")
    assert "--mapping was provided" not in trace


def test_cli_agent_orders_without_key_exits_zero(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "agent",
        "--source", str(ROOT / "sample_data/orders/source_orders.csv"),
        "--target", str(ROOT / "sample_data/orders/target_orders_clean.csv"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert "Source key: order_id" in result.stdout


def test_cli_agent_invalid_mapping_exits_non_zero_without_traceback(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "agent",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--mapping", str(tmp_path / "missing.yaml"),
        "--output-dir", str(tmp_path),
    ])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Traceback" not in combined
    assert (tmp_path / "agent_trace.json").exists()
    assert (tmp_path / "agent_report.md").exists()


def test_cli_deterministic_llm_summary_writes_file(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--key", "customer_id",
        "--llm-summary",
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode == 0
    assert (tmp_path / "llm_summary.md").exists()
    assert "LLM summary: skipped -" in result.stdout


def test_cli_agent_llm_summary_blocked_does_not_crash(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "agent",
        "--source", str(ROOT / "sample_data/crm_migration/source_contacts_salesforce.csv"),
        "--target", str(ROOT / "sample_data/crm_migration/target_contacts_dynamics_clean.csv"),
        "--llm-summary",
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode != 0
    assert "LLM summary: skipped - deterministic reconciliation did not execute" in result.stdout
