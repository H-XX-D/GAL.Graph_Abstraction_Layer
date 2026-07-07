import json

from gal_netlist.cli import main


def test_cli_doctor_outputs_human_report(capsys):
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out

    assert "version: 0.1.0" in out
    assert "dialects: " in out
    assert "schemas: " in out


def test_cli_doctor_outputs_json_report(capsys):
    assert main(["doctor", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)

    assert report["schema"] == "gal.doctor.v0"
    assert report["version"] == "0.1.0"
    assert report["checks"]["schemasRegistered"] is True
    assert report["checks"]["docsSchemasComplete"] is True
    assert "gal.verify_report.v0" in report["schemas"]
