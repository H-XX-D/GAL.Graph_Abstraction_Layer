from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_runbook_documents_non_publishing_gate():
    text = (ROOT / "RELEASE.md").read_text(encoding="utf-8")

    assert "python3 scripts/release_check.py" in text
    assert "It does not tag" in text
    assert "gh release create v0.1.0" in text
    assert "dist/SHA256SUMS" in text
    assert "gal-release-artifacts" in text
    assert "--notes-file dist/release-notes-v0.1.0.md" in text
    assert "python3 -m twine check" in text
    assert "dist/gal_netlist-0.1.0.tar.gz" in text


def test_readme_links_release_runbook():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "[RELEASE.md](RELEASE.md)" in text
