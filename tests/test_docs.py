from importlib.resources import files
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docs_index_links_schema_catalog():
    text = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert 'href="schemas/"' in text
    assert 'href="blog/"' in text
    assert "JSON Schemas" in (ROOT / "docs" / "schemas" / "index.html").read_text(encoding="utf-8")


def test_blog_drafts_reference_workspace_images():
    blog_dir = ROOT / "docs" / "blog"
    asset_dir = ROOT / "docs" / "assets" / "blog"
    drafts = sorted(blog_dir.glob("2026-07-07-*.md"))

    assert {path.name for path in drafts} == {
        "2026-07-07-gal-dialect-library.md",
        "2026-07-07-hal-boundary-discipline.md",
        "2026-07-07-mal-memory-graphs.md",
    }
    for draft in drafts:
        text = draft.read_text(encoding="utf-8")
        image_refs = [line for line in text.splitlines() if line.startswith("image: ")]
        assert len(image_refs) == 1
        image_path = (blog_dir / image_refs[0].removeprefix("image: ").strip()).resolve()
        assert image_path.is_relative_to(asset_dir.resolve())
        assert image_path.is_file()


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
