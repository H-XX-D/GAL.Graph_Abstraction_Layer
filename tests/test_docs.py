from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docs_index_links_schema_catalog():
    text = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert 'href="schemas/"' in text
    assert "JSON Schemas" in (ROOT / "docs" / "schemas" / "index.html").read_text(encoding="utf-8")


def test_schema_catalog_links_generated_schema_files():
    catalog = (ROOT / "docs" / "schemas" / "index.html").read_text(encoding="utf-8")

    for path in sorted((ROOT / "docs" / "schemas").glob("*.schema.json")):
        assert f'href="{path.name}"' in catalog
    assert 'href="index.json"' in catalog
