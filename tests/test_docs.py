from importlib.resources import files
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


def test_bundled_dialect_specs_match_docs_source():
    source_paths = sorted((ROOT / "docs" / "dialects").glob("*.md"))
    bundled = files("gal_netlist").joinpath("data", "dialects")

    assert [path.name for path in source_paths] == sorted(child.name for child in bundled.iterdir() if child.name.endswith(".md"))
    for source_path in source_paths:
        assert bundled.joinpath(source_path.name).read_text(encoding="utf-8") == source_path.read_text(encoding="utf-8")


def test_bundled_examples_match_source_examples():
    source_paths = sorted(path for path in (ROOT / "examples").rglob("*.gal") if path.is_file())

    for source_path in source_paths:
        relative = source_path.relative_to(ROOT / "examples")
        assert (
            files("gal_netlist").joinpath("data", "examples", *relative.parts).read_text(encoding="utf-8")
            == source_path.read_text(encoding="utf-8")
        )
