import json
from pathlib import Path

from gal_netlist.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_cli_verify_json_outputs_success_report(capsys):
    path = ROOT / "examples" / "minimal.mal.gal"

    assert main(["verify", str(path), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)

    assert report["ok"] is True
    assert report["path"] == str(path)
    assert report["dialect"] == "mal.v0"
    assert report["summary"] == {"entries": 11, "nodes": 1, "edges": 2, "nets": 2, "schedules": 2, "sets": 1}
    assert report["checks"] == {"parse": True, "semanticRoundtrip": True, "dialect": True, "components": True}
    assert report["skipped"] == []
    assert report["errors"] == []
    assert report["validation"] == []


def test_cli_verify_json_outputs_validation_report(tmp_path, capsys):
    path = tmp_path / "bad.gal"
    path.write_text("@gal netlist.v0\n@dialect mal.v0\nnet bad and2 weak\n", encoding="utf-8")

    assert main(["verify", str(path), "--dialect-dir", str(ROOT / "docs" / "dialects"), "--json"]) == 1
    report = json.loads(capsys.readouterr().out)

    assert report["ok"] is False
    assert report["checks"]["semanticRoundtrip"] is True
    assert report["checks"]["components"] is False
    assert report["validation"][0]["code"] == "wrong_arity"


def test_cli_verify_json_outputs_parse_errors(tmp_path, capsys):
    path = tmp_path / "bad.gal"
    path.write_text("@gal netlist.v0\nbody \"orphan\"\n", encoding="utf-8")

    assert main(["verify", str(path), "--json"]) == 1
    report = json.loads(capsys.readouterr().out)

    assert report["ok"] is False
    assert report["checks"]["parse"] is False
    assert report["skipped"] == []
    assert report["errors"][0]["code"] == "body_without_node"
