import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_check_help():
    result = subprocess.run(
        [sys.executable, "scripts/release_check.py", "--help"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Run the GAL 0.1.0 local release gate" in result.stdout
    assert "--allow-dirty" in result.stdout
