#!/usr/bin/env python3
"""Run the local release gate for GAL without tagging or publishing."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BUILD = ROOT / "build"


def read_pyproject_version() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return pyproject["project"]["version"]


VERSION = read_pyproject_version()
WHEEL = DIST / f"gal_netlist-{VERSION}-py3-none-any.whl"
RELEASE_NOTES = DIST / f"release-notes-v{VERSION}.md"
CHECKSUMS = DIST / "SHA256SUMS"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.version_only:
        validate_release_version(args.tag)
        print(f"release version ok: {VERSION}")
        return 0

    if not args.allow_dirty:
        require_clean_worktree()

    validate_release_version(args.tag)

    if not args.keep_build:
        remove_build_outputs()

    run([sys.executable, "-m", "pytest", "-q"])
    run([sys.executable, "-m", "build"])
    write_release_notes()
    check_distribution_artifacts()
    write_checksum_manifest()
    smoke_installed_wheel()
    smoke_checkout_cli()
    print_next_steps(args.tag)
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Run the GAL {VERSION} local release gate without tagging or publishing."
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="allow uncommitted changes while developing the release gate",
    )
    parser.add_argument(
        "--keep-build",
        action="store_true",
        help="reuse existing dist/ and build/ outputs instead of removing them first",
    )
    parser.add_argument(
        "--tag",
        default=f"v{VERSION}",
        help="tag name to print in the final release instructions",
    )
    parser.add_argument(
        "--version-only",
        action="store_true",
        help="only check release version consistency, then exit",
    )
    return parser.parse_args(argv)


def require_clean_worktree() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if status:
        raise SystemExit(
            "release check requires a clean worktree; commit or stash changes, "
            "or rerun with --allow-dirty while developing\n\n" + status
        )


def remove_build_outputs() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    shutil.rmtree(BUILD, ignore_errors=True)


def validate_release_version(tag: str) -> None:
    fallback_version = _regex_value(ROOT / "src" / "gal_netlist" / "_version.py", r'^FALLBACK_VERSION = "([^"]+)"$')
    changelog_version = _regex_value(ROOT / "CHANGELOG.md", r"^## ([0-9]+\.[0-9]+\.[0-9]+) - \d{4}-\d{2}-\d{2}$")

    expected = {
        "pyproject": VERSION,
        "fallback_version": fallback_version,
        "changelog": changelog_version,
        "tag": tag.removeprefix("v"),
    }
    versions = set(expected.values())
    if len(versions) != 1:
        details = "\n".join(f"{name}: {version}" for name, version in expected.items())
        raise SystemExit("release version mismatch\n\n" + details)


def _regex_value(path: Path, pattern: str) -> str:
    match = re.search(pattern, path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    if match is None:
        raise SystemExit(f"could not find release version in {path}")
    return match.group(1)


def check_distribution_artifacts() -> None:
    artifacts = distribution_artifacts()
    if not artifacts:
        raise SystemExit(f"no distribution artifacts found in {DIST}")
    run([sys.executable, "-m", "twine", "check", *map(str, artifacts)])


def distribution_artifacts() -> list[Path]:
    return sorted([*DIST.glob("*.whl"), *DIST.glob("*.tar.gz")])


def write_checksum_manifest() -> Path:
    artifacts = distribution_artifacts()
    if not artifacts:
        raise SystemExit(f"no distribution artifacts found in {DIST}")

    lines = []
    for artifact in artifacts:
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        lines.append(f"{digest}  {artifact.name}")
    CHECKSUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return CHECKSUMS


def write_release_notes() -> Path:
    RELEASE_NOTES.write_text(release_notes_for(VERSION), encoding="utf-8")
    return RELEASE_NOTES


def release_notes_for(version: str) -> str:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    pattern = rf"^## {re.escape(version)} - (?P<date>\d{{4}}-\d{{2}}-\d{{2}})\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, changelog, flags=re.MULTILINE | re.DOTALL)
    if match is None:
        raise SystemExit(f"could not find changelog notes for {version}")
    body = match.group("body").strip()
    return f"# GAL {version}\n\nReleased: {match.group('date')}\n\n{body}\n"


def smoke_installed_wheel() -> None:
    if not WHEEL.is_file():
        raise SystemExit(f"expected built wheel not found: {WHEEL}")

    with tempfile.TemporaryDirectory(prefix="gal-release-") as tmp:
        tmp_path = Path(tmp)
        venv = tmp_path / "venv"
        run([sys.executable, "-m", "venv", str(venv)])

        python = venv / "bin" / "python"
        gal = venv / "bin" / "gal"
        run([str(python), "-m", "pip", "install", str(WHEEL)])

        minimal = tmp_path / "minimal.mal.gal"
        minimal.write_text('@gal netlist.v0\n@dialect mal.v0\nclaim_1 "Claim" [kind: claim]\n', encoding="utf-8")

        run([str(gal), "--version"], cwd=tmp_path)
        assert_json_contains(
            [str(gal), "dialects", "--json"],
            '"mal.v0"',
            cwd=tmp_path,
        )
        assert_json_contains(
            [str(gal), "examples", "--dialect", "hal.v0", "--json"],
            '"dialects/hal.gal"',
            cwd=tmp_path,
        )
        run([str(gal), "examples", "--name", "minimal.mal.gal"], cwd=tmp_path, stdout=tmp_path / "copied.mal.gal")
        run([str(gal), "init", "starter.gal", "--dialect", "mal.v0", "--json"], cwd=tmp_path, quiet=True)
        run([str(gal), "verify", "starter.gal", "--json"], cwd=tmp_path, quiet=True)
        run([str(gal), "verify", "copied.mal.gal", "--json"], cwd=tmp_path, quiet=True)
        run([str(gal), "verify", "minimal.mal.gal", "--json"], cwd=tmp_path, quiet=True)


def smoke_checkout_cli() -> None:
    env = source_env()
    with tempfile.TemporaryDirectory(prefix="gal-checkout-") as tmp:
        tmp_path = Path(tmp)
        starter = tmp_path / "starter.gal"
        run([sys.executable, "-m", "gal_netlist.cli", "--version"], env=env)
        run([sys.executable, "-m", "gal_netlist.cli", "doctor", "--json"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "init", str(starter), "--dialect", "hal.v0", "--json"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "verify", str(starter), "--json"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "verify-all", "examples", "--json"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "schemas", "--json"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "convert", "examples/minimal.mal.gal", "--to", "json"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "convert", "examples/minimal.mal.gal", "--to", "dot"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "convert", "examples/minimal.mal.gal", "--to", "yaml"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "convert", "examples/minimal.mal.gal", "--to", "cypher"], env=env, quiet=True)
        run([sys.executable, "-m", "gal_netlist.cli", "load", "examples/minimal.mal.gal", "--mode", "plan"], env=env, quiet=True)


def source_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src if not existing else f"{src}{os.pathsep}{existing}"
    return env


def assert_json_contains(command: list[str], expected: str, *, cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
    if expected not in result.stdout:
        raise SystemExit(f"{command!r} output did not contain {expected!r}")


def run(
    command: list[str],
    *,
    cwd: Path = ROOT,
    stdout: Path | None = None,
    env: dict[str, str] | None = None,
    quiet: bool = False,
) -> None:
    print("+ " + " ".join(command), flush=True)
    if stdout is None:
        output = subprocess.DEVNULL if quiet else None
        subprocess.run(command, cwd=cwd, check=True, env=env, stdout=output)
        return
    with stdout.open("w", encoding="utf-8") as output:
        subprocess.run(command, cwd=cwd, check=True, stdout=output, env=env)


def print_next_steps(tag: str) -> None:
    print("\nRelease gate passed.")
    print("Manual release commands, after final review:")
    print(f"  git tag -a {tag} -m \"GAL {VERSION}\"")
    print(f"  git push origin {tag}")
    print(
        f"  gh release create {tag} dist/gal_netlist-{VERSION}.tar.gz "
        f"dist/gal_netlist-{VERSION}-py3-none-any.whl {CHECKSUMS.relative_to(ROOT)} "
        f"--title \"GAL {VERSION}\" --notes-file {RELEASE_NOTES.relative_to(ROOT)} --draft"
    )
    print(
        f"  python -m twine upload dist/gal_netlist-{VERSION}.tar.gz "
        f"dist/gal_netlist-{VERSION}-py3-none-any.whl"
    )


if __name__ == "__main__":
    raise SystemExit(main())
