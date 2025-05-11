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
    result = subprocess.run(
        ["python", "cli.py", "tests/sample.pdf", "-", "--format", "ynab", "--config", str(config_path)],
        capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "csv" in result.stdout or "error" not in result.stderr.lower()
