import os
import subprocess
import sys


def test_cli_help_exits_successfully() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    result = subprocess.run(
        [sys.executable, "-m", "data_reconciliation_agent.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "--source" in result.stdout
    assert "--target" in result.stdout
