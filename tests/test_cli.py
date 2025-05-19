import subprocess
import unittest
import json
import tempfile
from pathlib import Path

class TestCLI(unittest.TestCase):

    def test_cli_runs(self):
        # Stub subprocess call to just ensure CLI doesn't crash
        result = subprocess.run(
            ["python", "-m", "payslip2budget.cli", "tests/fixtures/sample.pdf", "--format", "ynab", "-"],
            capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "csv" in result.stdout or "error" not in result.stderr.lower()

    def test_format_and_api_config(self):
        result = subprocess.run(
            ["python", "-m", "payslip2budget.cli", "tests/fixtures/sample.pdf", "--api-config", "tests/fixtures/api-config.json", "--format", "ynab", "-"],
            capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "[WARN] Format is ignored when using an api-config" in result.stdout

if __name__ == '__main__':
    unittest.main()
