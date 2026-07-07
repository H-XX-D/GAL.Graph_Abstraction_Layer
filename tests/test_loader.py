import json
from pathlib import Path

from gal_netlist.cli import main
from gal_netlist.components import build_component_registry
from gal_netlist.dialects import load_registry
from gal_netlist.loader import load_document
from gal_netlist.parser import parse_text


ROOT = Path(__file__).resolve().parents[1]


def _document(path: str = "examples/minimal.mal.gal"):
    return parse_text((ROOT / path).read_text(encoding="utf-8"))


def _registry():
    return load_registry([ROOT / "docs" / "dialects"])


def test_plan_reports_actions_without_runtime():
    report = load_document(_document(), mode="plan", registry=_registry())
    assert report["ok"] is True
    assert report["mode"] == "plan"
    assert "runtime" not in report
    assert report["summary"] == {"nodes": 1, "edges": 2, "nets": 2, "schedules": 2, "sets": 1}
    assert report["actions"][0]["action"] == "create_node"
    assert any(action["action"] == "attach_edge" for action in report["actions"])


def test_replay_builds_fresh_runtime_state():
    report = load_document(_document(), mode="replay", registry=_registry())
    runtime = report["runtime"]
    assert report["ok"] is True
    assert "claim_ab12" in runtime["nodes"]
    assert len(runtime["edges"]) == 2
    assert "alert" in runtime["nets"]
    assert "watch0" in runtime["schedules"]
    assert runtime["sets"][0]["target"] == "watch0"


def test_merge_updates_existing_runtime():
    initial = load_document(_document(), mode="replay", registry=_registry())["runtime"]
    report = load_document(_document(), mode="merge", registry=_registry(), runtime=initial)
    assert report["ok"] is True
    assert report["actions"][0]["action"] == "update_node"
    assert any(action["action"] == "edge_exists" for action in report["actions"])
    assert len(report["runtime"]["edges"]) == 2


def test_verify_detects_missing_runtime_content():
    report = load_document(_document(), mode="verify", registry=_registry(), runtime={"schema": "gal.runtime.v0"})
    assert report["ok"] is False
    assert report["matches"] is False


def test_loader_reports_dialect_rejections():
    document = parse_text('@gal netlist.v0\n@dialect mal.v0\nbad "Bad" [kind: device]\n')
    report = load_document(document, mode="plan", registry=_registry())
    assert report["ok"] is False
    assert report["rejections"][0]["code"] == "unknown_node_kind"


def test_loader_reports_component_rejections():
    document = parse_text("@gal netlist.v0\n@dialect mal.v0\nnet bad and2 weak\n")
    report = load_document(
        document,
        mode="plan",
        registry=_registry(),
        component_registry=build_component_registry(_registry()),
    )
    assert report["ok"] is False
    assert report["rejections"][0]["code"] == "wrong_arity"


def test_cli_load_plan_outputs_json(capsys):
    path = ROOT / "examples" / "dialects" / "hal.gal"
    assert main(["load", str(path), "--mode", "plan"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["mode"] == "plan"
    assert report["summary"]["nodes"] == 3
    assert any(action["action"] == "create_net" for action in report["actions"])
