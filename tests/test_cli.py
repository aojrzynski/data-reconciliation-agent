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


def test_cli_agent_mode_exits_non_zero() -> None:
    result = _run_cli(["--mode", "agent"])
    assert result.returncode != 0
