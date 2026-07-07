import json
from pathlib import Path

from gal_netlist.cli import main
from gal_netlist.components import build_component_registry, validate_components
from gal_netlist.dialects import load_registry
from gal_netlist.parser import parse_text


ROOT = Path(__file__).resolve().parents[1]


def _registry():
    return load_registry([ROOT / "docs" / "dialects"])


def test_component_registry_builds_reusable_operations():
    components = build_component_registry(_registry())

    assert components.net_ops["and2"].arity == 2
    assert "mal.v0" in components.net_ops["and2"].sources
    assert "watch" in components.standing_ops
    assert components.standing_ops["watch"].threads_for("mal.v0") == {"tick"}


def test_component_validation_reports_wrong_net_arity():
    document = parse_text("@gal netlist.v0\n@dialect mal.v0\nnet bad and2 only_one\n")
    issues = validate_components(document, build_component_registry(_registry()))

    assert [issue.to_dict() for issue in issues] == [
        {
            "line": 3,
            "column": 1,
            "code": "wrong_arity",
            "message": "net component 'and2' expects 2 input(s), got 1",
            "text": "net bad and2 only_one",
        }
    ]


def test_component_validation_reports_unknown_operation():
    document = parse_text("@gal netlist.v0\n@dialect mal.v0\nnet bad mystery2 a b\n")
    issues = validate_components(document, build_component_registry(_registry()))

    assert issues[0].code == "unknown_component"
    assert "mystery2" in issues[0].message


def test_cli_components_json_lists_registry(capsys):
    assert main(["components", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["schema"] == "gal.components.v0"
    assert payload["netOps"]["and2"]["arity"] == 2
    assert "tick" in payload["standingOps"]["watch"]["threads"]


def test_cli_verify_uses_component_validation(tmp_path, capsys):
    path = tmp_path / "bad.gal"
    path.write_text("@gal netlist.v0\n@dialect mal.v0\nnet bad and2 weak\n", encoding="utf-8")

    assert main(["verify", str(path), "--dialect-dir", str(ROOT / "docs" / "dialects")]) == 1
    payload = json.loads(capsys.readouterr().err)
    assert payload["validation"][0]["code"] == "wrong_arity"
