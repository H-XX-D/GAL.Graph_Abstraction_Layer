from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_runbook_documents_non_publishing_gate():
    text = (ROOT / "RELEASE.md").read_text(encoding="utf-8")

    assert "python3 scripts/release_check.py" in text
    assert "It does not tag" in text
    assert "gh release create v0.1.0" in text
    assert "python3 -m twine check dist/*" in text


def test_readme_links_release_runbook():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "[RELEASE.md](RELEASE.md)" in text
