import json
from pathlib import Path

from gal_netlist.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_cli_init_creates_valid_default_mal_file(tmp_path, capsys):
    path = tmp_path / "starter.gal"

    assert main(["init", str(path)]) == 0
    out = capsys.readouterr().out

    assert out == f"created: {path}\n"
    assert path.read_text(encoding="utf-8") == (
        '@gal netlist.v0\n@dialect mal.v0\n\nclaim_1 "Starter claim" [kind: claim]\n'
    )
    assert main(["verify", str(path), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is True
    assert report["dialect"] == "mal.v0"


def test_cli_init_creates_valid_requested_dialect_file(tmp_path, capsys):
    path = tmp_path / "hal.gal"

    assert main(["init", str(path), "--dialect", "hal.v0"]) == 0
    capsys.readouterr()

    assert 'device_1 "Starter device" [kind: device]' in path.read_text(encoding="utf-8")
    assert main(["verify", str(path), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is True
    assert report["dialect"] == "hal.v0"


def test_cli_init_refuses_to_overwrite_without_force(tmp_path, capsys):
    path = tmp_path / "starter.gal"
    path.write_text("existing\n", encoding="utf-8")

    assert main(["init", str(path)]) == 1
    captured = capsys.readouterr()

    assert path.read_text(encoding="utf-8") == "existing\n"
    error = json.loads(captured.err)
    assert error == {"ok": False, "error": "file_exists", "path": str(path)}


def test_cli_init_force_overwrites_existing_file(tmp_path, capsys):
    path = tmp_path / "starter.gal"
    path.write_text("existing\n", encoding="utf-8")

    assert main(["init", str(path), "--force"]) == 0
    capsys.readouterr()

    assert path.read_text(encoding="utf-8").startswith("@gal netlist.v0\n@dialect mal.v0\n")


def test_cli_init_can_create_parent_directories(tmp_path, capsys):
    path = tmp_path / "nested" / "starter.gal"

    assert main(["init", str(path), "--parents"]) == 0
    capsys.readouterr()

    assert path.exists()


def test_cli_init_reports_unknown_dialect(tmp_path, capsys):
    path = tmp_path / "starter.gal"

    assert main(["init", str(path), "--dialect", "missing.v0"]) == 1
    captured = capsys.readouterr()

    assert not path.exists()
    assert json.loads(captured.err) == {"ok": False, "error": "unknown_dialect", "dialect": "missing.v0"}


def test_cli_init_honors_explicit_dialect_dir(tmp_path, capsys):
    path = tmp_path / "starter.gal"
    dialect_dir = ROOT / "docs" / "dialects"

    assert main(["init", str(path), "--dialect-dir", str(dialect_dir), "--dialect", "pal.v0"]) == 0
    capsys.readouterr()

    assert 'policy_1 "Starter policy" [kind: policy]' in path.read_text(encoding="utf-8")
