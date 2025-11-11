import subprocess
import sys
from pathlib import Path


def test_cli_integration_with_data_folder():
    data_dir = Path(__file__).parent / "data"
    config_file = data_dir / "loly.yml"

    result = subprocess.run(
        [sys.executable, "-m", "loly.cli", str(data_dir), f"--config={config_file}"],
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    assert result.returncode != 0, "Expected violations"

    assert "LY001" in output, "Expected LY001 violations to be detected"
    assert "Missing exc_info=True in exception handler" in output

    assert "LY002" in output, "Expected LY002 violations to be detected"
    assert "Logging in hot loop detected" in output

    assert "sample_exc_info.py" in output, "Expected violations from sample_exc_info.py"
    assert "sample_log_loop.py" in output, "Expected violations from sample_log_loop.py"
