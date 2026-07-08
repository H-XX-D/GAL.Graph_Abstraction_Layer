import subprocess
import sys
import tomllib
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


def test_release_check_runs_twine_check_and_dev_extra_includes_twine():
    script = (ROOT / "scripts" / "release_check.py").read_text(encoding="utf-8")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert '"twine", "check"' in script
    assert any(
        dependency.startswith("twine>=")
        for dependency in pyproject["project"]["optional-dependencies"]["dev"]
    )
