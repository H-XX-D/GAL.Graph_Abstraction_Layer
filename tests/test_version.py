import pytest

import gal_netlist
from gal_netlist.cli import main


def test_package_exports_version():
    assert gal_netlist.__version__ == "0.1.0"
    assert gal_netlist.package_version() == "0.1.0"


def test_cli_version_outputs_package_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])

    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "gal 0.1.0"
