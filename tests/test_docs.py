from importlib.resources import files
from pathlib import Path
import re

from gal_netlist.cli import main
from gal_netlist.dialects import default_dialect_dirs, load_registry


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


def test_documented_dialect_tables_match_registry():
    expected = load_registry(default_dialect_dirs(ROOT)).ids()

    for relative_path in ("README.md", "GAL_NETLIST_SPEC.md"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        dialect_ids = _dialect_table_ids(text)

        assert dialect_ids == expected
        assert dialect_ids == sorted(dialect_ids)


def test_spec_mal_example_verifies(tmp_path):
    spec = (ROOT / "GAL_NETLIST_SPEC.md").read_text(encoding="utf-8")
    match = re.search(r"## 11\. MAL Dialect Sketch.*?```gal\n(?P<gal>.*?)\n```", spec, re.DOTALL)
    assert match is not None

    path = tmp_path / "spec-mal-example.gal"
    path.write_text(match.group("gal"), encoding="utf-8")

    assert main(["verify", str(path), "--dialect-dir", str(ROOT / "docs" / "dialects")]) == 0


def _dialect_table_ids(text: str) -> list[str]:
    return re.findall(r"^\| `([^`]+\.v0)` \|", text, flags=re.MULTILINE)
