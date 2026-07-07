from pathlib import Path

from gal_netlist.cli import _semantic_document
from gal_netlist.parser import parse_text
from gal_netlist.renderer import render_document


ROOT = Path(__file__).resolve().parents[1]


def _example_paths() -> list[Path]:
    return sorted([ROOT / "examples" / "minimal.mal.gal", *(ROOT / "examples" / "dialects").glob("*.gal")])


def test_examples_parse_without_errors():
    for path in _example_paths():
        document = parse_text(path.read_text(encoding="utf-8"))
        assert document["errors"] == [], path
        assert document["entries"], path


def test_examples_semantic_roundtrip():
    for path in _example_paths():
        document = parse_text(path.read_text(encoding="utf-8"))
        rendered = render_document(document)
        reparsed = parse_text(rendered)
        assert reparsed["errors"] == [], path
        assert _semantic_document(reparsed) == _semantic_document(document), path


def test_structured_error_for_unknown_form():
    document = parse_text("not valid gal\n")
    assert document["errors"] == [
        {
            "line": 1,
            "column": 1,
            "code": "unknown_form",
            "message": "line matches no GAL form",
            "text": "not valid gal",
        }
    ]


def test_semantic_sources_survive_cli_cleaning():
    document = parse_text('node_a "A"\nrel> node_b(0.5)\n')
    clean = _semantic_document(document)
    assert clean["edges"][0]["source"] == "node_a"
