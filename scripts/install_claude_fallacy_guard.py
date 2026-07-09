from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLAUDE_HOME = Path.home() / ".claude"
FILES = (
    (Path(".claude/skills/fallacy-guard/SKILL.md"), Path("skills/fallacy-guard/SKILL.md")),
    (Path(".claude/skills/fallacy-guard/fallacy-catalog.md"), Path("skills/fallacy-guard/fallacy-catalog.md")),
    (Path(".claude/skills/fallacy-guard/math-guards.md"), Path("skills/fallacy-guard/math-guards.md")),
    (Path(".claude/commands/fallacy-guard.md"), Path("commands/fallacy-guard.md")),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install the Fallacy Guard Claude skill and command.")
    parser.add_argument(
        "--claude-home",
        type=Path,
        default=DEFAULT_CLAUDE_HOME,
        help="Claude config directory to install into. Defaults to ~/.claude.",
    )
    parser.add_argument("--check", action="store_true", help="Only verify that the installed files match.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without copying files.")
    parser.add_argument("--force", action="store_true", help="Overwrite differing installed files.")
    args = parser.parse_args(argv)

    try:
        return install(args.claude_home, check=args.check, dry_run=args.dry_run, force=args.force)
    except InstallError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


def install(claude_home: Path, *, check: bool = False, dry_run: bool = False, force: bool = False) -> int:
    claude_home = claude_home.expanduser()
    pairs = [(ROOT / source, claude_home / destination) for source, destination in FILES]
    states = [(source, destination, file_state(source, destination)) for source, destination in pairs]

    if check:
        for _, destination, state in states:
            print(f"{state}: {destination}")
        return 0 if all(state == "matches" for _, _, state in states) else 1

    differing = [destination for _, destination, state in states if state == "differs"]
    if differing and not force:
        paths = "\n".join(f"  {path}" for path in differing)
        raise InstallError(f"installed files differ; rerun with --force to overwrite:\n{paths}")

    for source, destination, state in states:
        if state == "matches":
            print(f"ok: {destination}")
            continue
        if dry_run:
            print(f"would install: {source.relative_to(ROOT)} -> {destination}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        print(f"installed: {destination}")

    if dry_run:
        print(f"dry run complete: {claude_home}")
    else:
        print(f"fallacy guard installed: {claude_home}")
    return 0


def file_state(source: Path, destination: Path) -> str:
    if not source.is_file():
        raise InstallError(f"missing source file: {source}")
    if not destination.exists():
        return "missing"
    if not destination.is_file():
        return "differs"
    if filecmp.cmp(source, destination, shallow=False):
        return "matches"
    return "differs"


class InstallError(Exception):
    pass


if __name__ == "__main__":
    raise SystemExit(main())
