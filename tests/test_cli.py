import subprocess
import json
import tempfile
from pathlib import Path

def test_cli_runs(monkeypatch):
    # Write dummy categories and config
    config = {
        "api_key": "fake-token",
        "budget_id": "budget-123",
        "account_id": "account-abc"
    }
    config_path = Path(tempfile.gettempdir()) / "test_config.json"
    config_path.write_text(json.dumps(config))

    # Stub subprocess call to just ensure CLI doesn't crash
    # ["python", "payslip2budget/cli.py", "tests/sample.pdf", "--format", "ynab", "--dry-run", "--api-config", str(config_path), "api"],
    result = subprocess.run(
        ["python", "-m", "payslip2budget.cli", "tests/sample.pdf", "--format", "ynab", "-"],
        capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "csv" in result.stdout or "error" not in result.stderr.lower()
