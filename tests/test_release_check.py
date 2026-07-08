import importlib.util
import hashlib
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_CHECK = ROOT / "scripts" / "release_check.py"


def load_release_check():
    spec = importlib.util.spec_from_file_location("release_check", RELEASE_CHECK)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    assert "--version-only" in result.stdout


def test_release_check_version_only_mode():
    result = subprocess.run(
        [sys.executable, "scripts/release_check.py", "--version-only"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert result.stdout.strip() == "release version ok: 0.1.0"


def test_release_check_runs_twine_check_and_dev_extra_includes_twine():
    script = RELEASE_CHECK.read_text(encoding="utf-8")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert '"twine", "check"' in script
    assert any(
        dependency.startswith("twine>=")
        for dependency in pyproject["project"]["optional-dependencies"]["dev"]
    )


def test_release_check_derives_version_from_pyproject():
    script = RELEASE_CHECK.read_text(encoding="utf-8")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    release_check = load_release_check()

    assert release_check.VERSION == pyproject["project"]["version"]
    assert 'VERSION = "0.1.0"' not in script


def test_release_check_validates_version_consistency():
    release_check = load_release_check()

    release_check.validate_release_version("v0.1.0")


def test_release_check_rejects_mismatched_tag():
    release_check = load_release_check()

    try:
        release_check.validate_release_version("v9.9.9")
    except SystemExit as exc:
        assert "release version mismatch" in str(exc)
        assert "tag: 9.9.9" in str(exc)
    else:
        raise AssertionError("expected mismatched tag to fail")


def test_release_check_extracts_version_release_notes():
    release_check = load_release_check()
    notes = release_check.release_notes_for("0.1.0")

    assert notes.startswith("# GAL 0.1.0\n\nReleased: 2026-07-08\n")
    assert "### Added" in notes
    assert "## 0.1.0" not in notes


def test_release_check_writes_version_release_notes(tmp_path, monkeypatch):
    release_check = load_release_check()
    notes_path = tmp_path / "release-notes.md"
    monkeypatch.setattr(release_check, "RELEASE_NOTES", notes_path)

    assert release_check.write_release_notes() == notes_path
    assert notes_path.read_text(encoding="utf-8").startswith("# GAL 0.1.0")


def test_release_check_writes_checksum_manifest(tmp_path, monkeypatch):
    release_check = load_release_check()
    dist = tmp_path / "dist"
    dist.mkdir()
    sdist = dist / "gal_netlist-0.1.0.tar.gz"
    wheel = dist / "gal_netlist-0.1.0-py3-none-any.whl"
    sdist.write_bytes(b"sdist")
    wheel.write_bytes(b"wheel")
    checksums = dist / "SHA256SUMS"
    monkeypatch.setattr(release_check, "DIST", dist)
    monkeypatch.setattr(release_check, "CHECKSUMS", checksums)

    assert release_check.write_checksum_manifest() == checksums
    assert checksums.read_text(encoding="utf-8").splitlines() == [
        f"{hashlib.sha256(wheel.read_bytes()).hexdigest()}  {wheel.name}",
        f"{hashlib.sha256(sdist.read_bytes()).hexdigest()}  {sdist.name}",
    ]


def test_ci_runs_release_version_check():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "python scripts/release_check.py --version-only" in workflow


def test_ci_checks_only_distribution_artifacts():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "python -m twine check dist/*.whl dist/*.tar.gz" in workflow
    assert "python -m twine check dist/*\n" not in workflow
