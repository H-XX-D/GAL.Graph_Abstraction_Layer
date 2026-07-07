import json

from gal_netlist.cli import main
from gal_netlist.schemas import get_schema, schema_ids, schema_index


def test_schema_registry_lists_core_contracts():
    assert schema_ids() == [
        "gal.components.v0",
        "gal.dialects.v0",
        "gal.netlist.ast.v0",
        "gal.runtime.v0",
        "gal.verify_batch.v0",
        "gal.verify_report.v0",
    ]
    assert schema_index()["schema"] == "gal.schemas.v0"
    assert get_schema("gal.verify_report.v0")["$id"] == "gal.verify_report.v0"


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
