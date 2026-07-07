import json
from pathlib import Path

from jsonschema import Draft202012Validator

from gal_netlist.cli import main
from gal_netlist.schemas import get_schema, schema_filename, schema_ids, schema_index, write_schemas


ROOT = Path(__file__).resolve().parents[1]


def _cli_json(args: list[str], capsys):
    assert main(args) == 0
    return json.loads(capsys.readouterr().out)


def test_schema_registry_lists_core_contracts():
    assert schema_ids() == [
        "gal.components.v0",
        "gal.dialects.v0",
        "gal.doctor.v0",
        "gal.examples.v0",
        "gal.init_report.v0",
        "gal.netlist.ast.v0",
        "gal.runtime.v0",
        "gal.verify_batch.v0",
        "gal.verify_report.v0",
    ]
    assert schema_index()["schema"] == "gal.schemas.v0"
    assert get_schema("gal.verify_report.v0")["$id"] == "gal.verify_report.v0"
    assert schema_filename("gal.verify_report.v0") == "gal.verify_report.v0.schema.json"


def test_all_schemas_are_valid_json_schemas():
    for schema_id in schema_ids():
        Draft202012Validator.check_schema(get_schema(schema_id))


def test_get_schema_returns_copy():
    schema = get_schema("gal.verify_report.v0")
    schema["$id"] = "changed"

    assert get_schema("gal.verify_report.v0")["$id"] == "gal.verify_report.v0"


def test_cli_schemas_lists_ids(capsys):
    assert main(["schemas"]) == 0
    out = capsys.readouterr().out

    assert "gal.verify_report.v0" in out
    assert "gal.verify_batch.v0" in out


def test_cli_schemas_json_outputs_index(capsys):
    assert main(["schemas", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["schema"] == "gal.schemas.v0"
    assert payload["schemas"][0]["id"] == "gal.components.v0"


def test_cli_schemas_outputs_named_schema(capsys):
    assert main(["schemas", "gal.verify_batch.v0"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["$id"] == "gal.verify_batch.v0"
    assert payload["properties"]["schema"]["const"] == "gal.verify_batch.v0"


def test_cli_schemas_reports_unknown_schema(capsys):
    assert main(["schemas", "missing.v0"]) == 1
    payload = json.loads(capsys.readouterr().err)

    assert payload == {"ok": False, "error": "unknown_schema", "schema": "missing.v0"}


def test_write_schemas_exports_index_and_schema_files(tmp_path):
    written = write_schemas(tmp_path)

    assert written is not None
    assert (tmp_path / "index.json").exists()
    assert (tmp_path / "gal.verify_report.v0.schema.json").exists()
    assert json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))["schema"] == "gal.schemas.v0"
    assert json.loads((tmp_path / "gal.verify_report.v0.schema.json").read_text(encoding="utf-8"))["$id"] == "gal.verify_report.v0"


def test_cli_schemas_write_dir_exports_files(tmp_path, capsys):
    assert main(["schemas", "--write-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out

    assert "index.json" in out
    assert "gal.verify_batch.v0.schema.json" in out
    assert (tmp_path / "gal.verify_batch.v0.schema.json").exists()


def test_cli_schemas_write_dir_exports_single_schema(tmp_path, capsys):
    assert main(["schemas", "gal.verify_report.v0", "--write-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out

    assert "gal.verify_report.v0.schema.json" in out
    assert not (tmp_path / "index.json").exists()
    assert json.loads((tmp_path / "gal.verify_report.v0.schema.json").read_text(encoding="utf-8"))["$id"] == "gal.verify_report.v0"


def test_docs_schemas_are_in_sync_with_registry():
    docs_dir = ROOT / "docs" / "schemas"

    assert json.loads((docs_dir / "index.json").read_text(encoding="utf-8")) == schema_index()
    for schema_id in schema_ids():
        assert json.loads((docs_dir / schema_filename(schema_id)).read_text(encoding="utf-8")) == get_schema(schema_id)


def test_cli_payloads_validate_against_published_schemas(tmp_path, capsys):
    Draft202012Validator(get_schema("gal.dialects.v0")).validate(_cli_json(["dialects", "--json"], capsys))
    Draft202012Validator(get_schema("gal.components.v0")).validate(_cli_json(["components", "--json"], capsys))
    Draft202012Validator(get_schema("gal.doctor.v0")).validate(_cli_json(["doctor", "--json"], capsys))
    Draft202012Validator(get_schema("gal.examples.v0")).validate(_cli_json(["examples", "--json"], capsys))
    Draft202012Validator(get_schema("gal.init_report.v0")).validate(
        _cli_json(["init", str(tmp_path / "starter.gal"), "--json"], capsys)
    )
    Draft202012Validator(get_schema("gal.verify_report.v0")).validate(
        _cli_json(["verify", "examples/minimal.mal.gal", "--json"], capsys)
    )
    Draft202012Validator(get_schema("gal.verify_batch.v0")).validate(_cli_json(["verify-all", "examples", "--json"], capsys))
    Draft202012Validator(get_schema("gal.netlist.ast.v0")).validate(
        _cli_json(["parse", "examples/minimal.mal.gal", "--json"], capsys)
    )


def test_loader_runtime_validates_against_runtime_schema(capsys):
    report = _cli_json(["load", "examples/minimal.mal.gal", "--mode", "replay"], capsys)

    Draft202012Validator(get_schema("gal.runtime.v0")).validate(report["runtime"])
