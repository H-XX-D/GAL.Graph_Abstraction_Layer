import json
from pathlib import Path

from jsonschema import Draft202012Validator

from gal_netlist.cli import main
from gal_netlist.schemas import get_schema


ROOT = Path(__file__).resolve().parents[1]


def test_cli_examples_lists_bundled_examples(capsys):
    assert main(["examples"]) == 0
    out = capsys.readouterr().out

    assert "minimal.mal.gal dialect=mal.v0" in out
    assert "dialects/hal.gal dialect=hal.v0" in out


def test_cli_examples_json_outputs_registry(capsys):
    assert main(["examples", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    Draft202012Validator(get_schema("gal.examples.v0")).validate(payload)
    assert payload["schema"] == "gal.examples.v0"
    assert {"name": "minimal.mal.gal", "dialect": "mal.v0"} in payload["examples"]
    assert {"name": "dialects/hal.gal", "dialect": "hal.v0"} in payload["examples"]


def test_cli_examples_prints_named_example(capsys):
    assert main(["examples", "--name", "minimal.mal.gal"]) == 0
    out = capsys.readouterr().out

    assert out.startswith("@gal netlist.v0\n@dialect mal.v0\n")


def test_cli_examples_json_filters_named_example(capsys):
    assert main(["examples", "--name", "dialects/hal.gal", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    Draft202012Validator(get_schema("gal.examples.v0")).validate(payload)
    assert payload["examples"] == [{"name": "dialects/hal.gal", "dialect": "hal.v0"}]


def test_cli_examples_reports_unknown_name(capsys):
    assert main(["examples", "--name", "missing.gal"]) == 1
    payload = json.loads(capsys.readouterr().err)

    assert payload == {"ok": False, "error": "unknown_example", "name": "missing.gal"}


def test_cli_examples_writes_all_examples(tmp_path, capsys):
    assert main(["examples", "--write-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out

    assert "minimal.mal.gal" in out
    assert (tmp_path / "minimal.mal.gal").exists()
    assert (tmp_path / "dialects" / "hal.gal").exists()
    assert main(["verify-all", str(tmp_path), "--json"]) == 0


def test_cli_examples_writes_named_example_as_json(tmp_path, capsys):
    assert main(["examples", "--name", "dialects/hal.gal", "--write-dir", str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    Draft202012Validator(get_schema("gal.examples.v0")).validate(payload)
    assert payload["examples"] == [{"name": "dialects/hal.gal", "dialect": "hal.v0"}]
    assert payload["written"] == [str(tmp_path / "dialects" / "hal.gal")]
    assert (tmp_path / "dialects" / "hal.gal").exists()


def test_cli_examples_refuses_to_overwrite_without_force(tmp_path, capsys):
    path = tmp_path / "minimal.mal.gal"
    path.write_text("existing\n", encoding="utf-8")

    assert main(["examples", "--name", "minimal.mal.gal", "--write-dir", str(tmp_path)]) == 1
    payload = json.loads(capsys.readouterr().err)

    assert payload == {"ok": False, "error": "file_exists", "path": str(path)}
    assert path.read_text(encoding="utf-8") == "existing\n"


def test_cli_examples_force_overwrites(tmp_path, capsys):
    path = tmp_path / "minimal.mal.gal"
    path.write_text("existing\n", encoding="utf-8")

    assert main(["examples", "--name", "minimal.mal.gal", "--write-dir", str(tmp_path), "--force"]) == 0
    capsys.readouterr()

    assert path.read_text(encoding="utf-8").startswith("@gal netlist.v0\n@dialect mal.v0\n")
