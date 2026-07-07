from pathlib import Path

from gal_netlist.cli import main
from gal_netlist.converters import to_dot, to_yaml
from gal_netlist.parser import parse_text


ROOT = Path(__file__).resolve().parents[1]


def test_dot_conversion_includes_nodes_edges_nets_and_schedules():
    document = parse_text((ROOT / "examples" / "minimal.mal.gal").read_text(encoding="utf-8"))
    dot = to_dot(document)
    assert dot.startswith("digraph G {\n")
    assert 'claim_ab12 [label="API is degraded"' in dot
    assert 'claim_ab12 -> service_api [label="concerns 0.9"' in dot
    assert 'gal_net_alert [shape="box", label="net alert or2", _gal_form="net"]' in dot
    assert 'gal_schedule_watch0 [shape="box", label="watch0 tick"' in dot


def test_yaml_conversion_includes_semantic_ast_shape():
    document = parse_text((ROOT / "examples" / "dialects" / "hal.gal").read_text(encoding="utf-8"))
    yaml = to_yaml(document)
    assert "schema: gal.netlist.ast.v0\n" in yaml
    assert "dialect: hal.v0\n" in yaml
    assert 'label: "GPU device 0"\n' in yaml
    assert "relation: attached_to\n" in yaml


def test_cli_convert_dot_and_yaml(capsys):
    hal_path = ROOT / "examples" / "dialects" / "hal.gal"

    assert main(["convert", str(hal_path), "--to", "dot"]) == 0
    dot_out = capsys.readouterr().out
    assert "digraph G" in dot_out
    assert "device_gpu0 -> bus_pcie0" in dot_out

    assert main(["convert", str(hal_path), "--to", "yaml"]) == 0
    yaml_out = capsys.readouterr().out
    assert "dialect: hal.v0" in yaml_out
    assert "nodes:" in yaml_out


def test_all_examples_convert_to_dot_and_yaml():
    paths = sorted([ROOT / "examples" / "minimal.mal.gal", *(ROOT / "examples" / "dialects").glob("*.gal")])
    for path in paths:
        document = parse_text(path.read_text(encoding="utf-8"))
        assert to_dot(document).startswith("digraph G {\n"), path
        assert "schema: gal.netlist.ast.v0\n" in to_yaml(document), path
