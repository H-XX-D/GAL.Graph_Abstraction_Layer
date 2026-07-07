"""Package version helpers."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


PACKAGE_NAME = "gal-netlist"
FALLBACK_VERSION = "0.1.0"


def package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return FALLBACK_VERSION


__version__ = package_version()
