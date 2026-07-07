"""Command line interface for GAL:netlist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .dialects import default_dialect_dirs, load_registry, validate_document
from .parser import parse_text
from .renderer import render_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gal")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser("parse", help="parse GAL text")
    parse_cmd.add_argument("path", type=Path)
    parse_cmd.add_argument("--json", action="store_true", help="emit JSON AST")

    format_cmd = subparsers.add_parser("format", help="render canonical GAL text")
    format_cmd.add_argument("path", type=Path)

    verify_cmd = subparsers.add_parser("verify", help="parse and semantic round-trip a GAL file")
    verify_cmd.add_argument("path", type=Path)
    verify_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")
    verify_cmd.add_argument("--no-dialect", action="store_true", help="skip dialect vocabulary validation")

    dialects_cmd = subparsers.add_parser("dialects", help="list available dialect specs")
    dialects_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")

    convert_cmd = subparsers.add_parser("convert", help="convert GAL to another representation")
    convert_cmd.add_argument("path", type=Path)
    convert_cmd.add_argument("--to", choices=["json"], required=True)

    args = parser.parse_args(argv)
    if args.command == "dialects":
        registry = load_registry(args.dialect_dir or default_dialect_dirs(Path.cwd()))
        for dialect_id in registry.ids():
            print(dialect_id)
        return 0

    text = args.path.read_text(encoding="utf-8")
    document = parse_text(text)
    if document["errors"]:
        print(json.dumps({"ok": False, "errors": document["errors"]}, indent=2), file=sys.stderr)
        return 1

    if args.command == "parse":
        if args.json:
            print(json.dumps(_semantic_document(document), indent=2, sort_keys=True))
        else:
            print(f"ok: {len(document['entries'])} entries")
        return 0

    if args.command == "format":
        sys.stdout.write(render_document(document))
        return 0

    if args.command == "verify":
        rendered = render_document(document)
        reparsed = parse_text(rendered)
        if reparsed["errors"]:
            print(json.dumps({"ok": False, "errors": reparsed["errors"]}, indent=2), file=sys.stderr)
            return 1
        if _semantic_document(document) != _semantic_document(reparsed):
            print(json.dumps({"ok": False, "error": "semantic_roundtrip_failed"}, indent=2), file=sys.stderr)
            return 1
        if not args.no_dialect:
            registry = load_registry(args.dialect_dir or default_dialect_dirs(args.path))
            validation_issues = validate_document(document, registry)
            if validation_issues:
                print(
                    json.dumps({"ok": False, "validation": [issue.to_dict() for issue in validation_issues]}, indent=2),
                    file=sys.stderr,
                )
                return 1
        print(f"ok: {args.path}")
        return 0

    if args.command == "convert":
        print(json.dumps(_semantic_document(document), indent=2, sort_keys=True))
        return 0

    return 2


def _semantic_document(document: dict) -> dict:
    def clean(value):
        if isinstance(value, dict):
            return {
                key: clean(inner)
                for key, inner in value.items()
                if key not in {"line", "source_text", "comments", "errors"}
            }
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    return clean(document)


if __name__ == "__main__":
    raise SystemExit(main())
