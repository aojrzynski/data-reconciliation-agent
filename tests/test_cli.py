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
    assert "Matched keys:" in result.stdout


def test_cli_missing_key_exits_non_zero(tmp_path: Path) -> None:
    result = _run_cli([
        "--mode", "deterministic",
        "--source", str(ROOT / "sample_data/customers/source_customers.csv"),
        "--target", str(ROOT / "sample_data/customers/target_customers_clean.csv"),
        "--output-dir", str(tmp_path),
    ])
    assert result.returncode != 0


def test_cli_agent_mode_exits_non_zero() -> None:
    result = _run_cli(["--mode", "agent"])
    assert result.returncode != 0
    assert "not implemented" in (result.stdout + result.stderr).lower()


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
