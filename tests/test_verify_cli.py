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


def test_cli_verify_all_json_outputs_batch_report(capsys):
    minimal = ROOT / "examples" / "minimal.mal.gal"
    hal = ROOT / "examples" / "dialects" / "hal.gal"

    assert main(["verify-all", str(minimal), str(hal), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)

    assert report["schema"] == "gal.verify_batch.v0"
    assert report["ok"] is True
    assert report["count"] == 2
    assert report["passed"] == 2
    assert report["failed"] == 0
    assert [entry["path"] for entry in report["reports"]] == [str(hal), str(minimal)]


def test_cli_verify_all_json_reports_mixed_failures(tmp_path, capsys):
    good = ROOT / "examples" / "minimal.mal.gal"
    bad = tmp_path / "bad.gal"
    bad.write_text("@gal netlist.v0\n@dialect mal.v0\nnet bad and2 weak\n", encoding="utf-8")

    assert main(["verify-all", str(good), str(bad), "--dialect-dir", str(ROOT / "docs" / "dialects"), "--json"]) == 1
    report = json.loads(capsys.readouterr().out)

    assert report["ok"] is False
    assert report["count"] == 2
    assert report["passed"] == 1
    assert report["failed"] == 1
    failed = [entry for entry in report["reports"] if not entry["ok"]]
    assert failed[0]["validation"][0]["code"] == "wrong_arity"


def test_cli_verify_all_expands_directories(capsys):
    dialect_dir = ROOT / "examples" / "dialects"

    assert main(["verify-all", str(dialect_dir)]) == 0
    out = capsys.readouterr().out

    assert "summary: 21 passed, 0 failed, 21 total" in out
    assert "ok: " in out
