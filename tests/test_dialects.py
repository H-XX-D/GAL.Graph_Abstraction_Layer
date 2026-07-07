import json
from pathlib import Path

from gal_netlist.cli import main
from gal_netlist.dialects import default_dialect_dirs, load_registry, validate_document
from gal_netlist.parser import parse_text


ROOT = Path(__file__).resolve().parents[1]


def test_registry_loads_markdown_vocabularies():
    registry = load_registry([ROOT / "docs" / "dialects"])
    assert "mal.v0" in registry.ids()
    assert "hal.v0" in registry.ids()
    assert registry.get("hal.v0")["nodeKinds"][0] == "device"
    payload = registry.to_dict()
    assert payload["schema"] == "gal.dialects.v0"
    assert payload["dialects"]["mal.v0"]["signals"][0] == "weak"


def test_examples_validate_against_declared_dialects():
    registry = load_registry([ROOT / "docs" / "dialects"])
    paths = sorted([ROOT / "examples" / "minimal.mal.gal", *(ROOT / "examples" / "dialects").glob("*.gal")])
    for path in paths:
        document = parse_text(path.read_text(encoding="utf-8"))
        assert validate_document(document, registry) == [], path


def test_unknown_node_kind_reports_structured_validation_issue():
    registry = load_registry([ROOT / "docs" / "dialects"])
    document = parse_text('@gal netlist.v0\n@dialect mal.v0\nbad "Bad" [kind: device]\n')
    issues = validate_document(document, registry)
    assert [issue.to_dict() for issue in issues] == [
        {
            "line": 3,
            "column": 1,
            "code": "unknown_node_kind",
            "message": "node kind 'device' is not allowed by mal.v0",
            "text": 'bad "Bad" [kind: device]',
        }
    ]


def test_unknown_signal_reports_structured_validation_issue():
    registry = load_registry([ROOT / "docs" / "dialects"])
    document = parse_text("@gal netlist.v0\n@dialect mal.v0\nnet alert or2 high_concern mystery_signal\n")
    issues = validate_document(document, registry)
    assert [issue.to_dict() for issue in issues] == [
        {
            "line": 3,
            "column": 1,
            "code": "unknown_signal",
            "message": "signal 'mystery_signal' is not allowed by mal.v0",
            "text": "net alert or2 high_concern mystery_signal",
        }
    ]


def test_net_inputs_can_reference_declared_graph_symbols():
    registry = load_registry([ROOT / "docs" / "dialects"])
    document = parse_text(
        '@gal netlist.v0\n@dialect mal.v0\nclaim_ab12 "Claim" [kind: claim]\nnet alert or2 claim_ab12 route\nnet route not1 alert\n'
    )
    assert validate_document(document, registry) == []


def test_default_dialect_dirs_finds_repo_docs():
    candidates = default_dialect_dirs(ROOT / "examples" / "minimal.mal.gal")
    assert ROOT / "docs" / "dialects" in candidates


def test_default_dialect_dirs_include_bundled_specs_outside_repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    candidates = default_dialect_dirs(tmp_path / "minimal.mal.gal")
    registry = load_registry(candidates)
    assert "mal.v0" in registry.ids()
    assert "hal.v0" in registry.ids()


def test_cli_dialects_json_outputs_registry(capsys):
    assert main(["dialects", "--dialect-dir", str(ROOT / "docs" / "dialects"), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "gal.dialects.v0"
    assert payload["dialects"]["hal.v0"]["nodeKinds"][0] == "device"
