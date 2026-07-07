"""Command line interface for GAL:netlist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .components import build_component_registry, validate_components
from .converters import to_cypher, to_dot, to_yaml
from .dialects import default_dialect_dirs, load_registry, validate_document
from .loader import LOAD_MODES, load_document
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
    verify_cmd.add_argument("--json", action="store_true", help="emit JSON verification report")

    verify_all_cmd = subparsers.add_parser("verify-all", help="verify GAL files or directories")
    verify_all_cmd.add_argument("targets", type=Path, nargs="+")
    verify_all_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")
    verify_all_cmd.add_argument("--no-dialect", action="store_true", help="skip dialect vocabulary validation")
    verify_all_cmd.add_argument("--json", action="store_true", help="emit JSON batch verification report")

    dialects_cmd = subparsers.add_parser("dialects", help="list available dialect specs")
    dialects_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")
    dialects_cmd.add_argument("--json", action="store_true", help="emit JSON dialect registry")

    components_cmd = subparsers.add_parser("components", help="list registered net and standing operation components")
    components_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")
    components_cmd.add_argument("--kind", choices=["all", "net-op", "standing-op"], default="all")
    components_cmd.add_argument("--json", action="store_true", help="emit JSON component registry")

    convert_cmd = subparsers.add_parser("convert", help="convert GAL to another representation")
    convert_cmd.add_argument("path", type=Path)
    convert_cmd.add_argument("--from", dest="from_format", choices=["gal", "json"], default="gal")
    convert_cmd.add_argument("--to", choices=["gal", "json", "dot", "yaml", "cypher"], required=True)

    load_cmd = subparsers.add_parser("load", help="load GAL into an in-memory runtime report")
    load_cmd.add_argument("path", type=Path)
    load_cmd.add_argument("--mode", choices=sorted(LOAD_MODES), required=True)
    load_cmd.add_argument("--runtime-json", type=Path, help="existing runtime JSON for verify or merge")
    load_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")
    load_cmd.add_argument("--no-dialect", action="store_true", help="skip dialect vocabulary validation")

    args = parser.parse_args(argv)
    if args.command == "dialects":
        registry = load_registry(args.dialect_dir or default_dialect_dirs(Path.cwd()))
        if args.json:
            print(json.dumps(registry.to_dict(), indent=2, sort_keys=True))
            return 0
        for dialect_id in registry.ids():
            print(dialect_id)
        return 0

    if args.command == "components":
        registry = load_registry(args.dialect_dir or default_dialect_dirs(Path.cwd()))
        components = build_component_registry(registry)
        if args.json:
            payload = components.to_dict()
            if args.kind == "net-op":
                payload["standingOps"] = {}
            elif args.kind == "standing-op":
                payload["netOps"] = {}
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        if args.kind in {"all", "net-op"}:
            for name, component in sorted(components.net_ops.items()):
                print(f"net_op {name} arity={component.arity} sources={','.join(sorted(component.sources))}")
        if args.kind in {"all", "standing-op"}:
            for name, component in sorted(components.standing_ops.items()):
                threads = ",".join(sorted(component.threads_for(None)))
                print(f"standing_op {name} threads={threads} sources={','.join(sorted(component.sources))}")
        return 0

    if args.command == "verify-all":
        paths = _expand_verify_targets(args.targets)
        reports = [
            _verify_path(path, dialect_dirs=args.dialect_dir or default_dialect_dirs(path), no_dialect=args.no_dialect)
            for path in paths
        ]
        payload = _batch_report(reports)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for report in reports:
                print(f"{'ok' if report['ok'] else 'fail'}: {report['path']}")
            print(f"summary: {payload['passed']} passed, {payload['failed']} failed, {payload['count']} total")
        return 0 if payload["ok"] else 1

    text = args.path.read_text(encoding="utf-8")
    if args.command == "convert" and args.from_format == "json":
        document = json.loads(text)
    else:
        document = parse_text(text)
        if document["errors"]:
            payload = _verify_parse_error(args.path, document) if args.command == "verify" else {"ok": False, "errors": document["errors"]}
            if args.command == "verify" and args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(json.dumps(payload, indent=2), file=sys.stderr)
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
        report = _verify_report(
            document,
            path=args.path,
            dialect_dirs=args.dialect_dir or default_dialect_dirs(args.path),
            no_dialect=args.no_dialect,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["ok"] else 1
        if report.get("errors"):
            print(json.dumps({"ok": False, "errors": report["errors"]}, indent=2), file=sys.stderr)
            return 1
        if report.get("error"):
            print(json.dumps({"ok": False, "error": report["error"]}, indent=2), file=sys.stderr)
            return 1
        if report.get("validation"):
            print(json.dumps({"ok": False, "validation": report["validation"]}, indent=2), file=sys.stderr)
            return 1
        print(f"ok: {args.path}")
        return 0

    if args.command == "convert":
        semantic_document = _semantic_document(document)
        if args.to == "gal":
            sys.stdout.write(render_document(semantic_document))
        elif args.to == "json":
            print(json.dumps(semantic_document, indent=2, sort_keys=True))
        elif args.to == "dot":
            sys.stdout.write(to_dot(semantic_document))
        elif args.to == "yaml":
            sys.stdout.write(to_yaml(semantic_document))
        elif args.to == "cypher":
            sys.stdout.write(to_cypher(semantic_document))
        return 0

    if args.command == "load":
        runtime = None
        if args.runtime_json is not None:
            runtime = json.loads(args.runtime_json.read_text(encoding="utf-8"))
        registry = None if args.no_dialect else load_registry(args.dialect_dir or default_dialect_dirs(args.path))
        component_registry = None if registry is None else build_component_registry(registry)
        report = load_document(
            _semantic_document(document),
            mode=args.mode,
            registry=registry,
            component_registry=component_registry,
            runtime=runtime,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["ok"] else 1

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


def _verify_parse_error(path: Path, document: dict) -> dict:
    return {
        "ok": False,
        "path": str(path),
        "schema": document.get("schema"),
        "dialect": document.get("dialect"),
        "summary": _summary(document),
        "checks": {
            "parse": False,
            "semanticRoundtrip": False,
            "dialect": False,
            "components": False,
        },
        "skipped": [],
        "errors": document["errors"],
        "validation": [],
    }


def _verify_path(path: Path, *, dialect_dirs: list[Path], no_dialect: bool) -> dict:
    try:
        document = parse_text(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return _read_error(path, exc)
    if document["errors"]:
        return _verify_parse_error(path, document)
    return _verify_report(document, path=path, dialect_dirs=dialect_dirs, no_dialect=no_dialect)


def _verify_report(document: dict, *, path: Path, dialect_dirs: list[Path], no_dialect: bool) -> dict:
    report = {
        "ok": True,
        "path": str(path),
        "schema": document.get("schema"),
        "dialect": document.get("dialect"),
        "summary": _summary(document),
        "checks": {
            "parse": True,
            "semanticRoundtrip": False,
            "dialect": False,
            "components": False,
        },
        "skipped": [],
        "errors": [],
        "validation": [],
    }

    rendered = render_document(document)
    reparsed = parse_text(rendered)
    if reparsed["errors"]:
        report["ok"] = False
        report["errors"] = reparsed["errors"]
        return report
    if _semantic_document(document) != _semantic_document(reparsed):
        report["ok"] = False
        report["error"] = "semantic_roundtrip_failed"
        return report
    report["checks"]["semanticRoundtrip"] = True

    if no_dialect:
        report["skipped"] = ["dialect", "components"]
        return report

    registry = load_registry(dialect_dirs)
    dialect_issues = validate_document(document, registry)
    report["checks"]["dialect"] = not dialect_issues
    component_issues = validate_components(document, build_component_registry(registry))
    report["checks"]["components"] = not component_issues
    validation_issues = [*dialect_issues, *component_issues]
    if validation_issues:
        report["ok"] = False
        report["validation"] = [issue.to_dict() for issue in validation_issues]

    return report


def _read_error(path: Path, exc: OSError) -> dict:
    return {
        "ok": False,
        "path": str(path),
        "schema": None,
        "dialect": None,
        "summary": _summary({}),
        "checks": {
            "parse": False,
            "semanticRoundtrip": False,
            "dialect": False,
            "components": False,
        },
        "skipped": [],
        "errors": [
            {
                "line": 1,
                "column": 1,
                "code": "read_error",
                "message": str(exc),
                "text": str(path),
            }
        ],
        "validation": [],
    }


def _expand_verify_targets(targets: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for target in targets:
        if target.is_dir():
            paths.extend(sorted(path for path in target.rglob("*.gal") if path.is_file()))
        else:
            paths.append(target)
    return sorted(dict.fromkeys(paths), key=lambda path: str(path))


def _batch_report(reports: list[dict]) -> dict:
    failed = [report for report in reports if not report["ok"]]
    return {
        "schema": "gal.verify_batch.v0",
        "ok": not failed,
        "count": len(reports),
        "passed": len(reports) - len(failed),
        "failed": len(failed),
        "reports": reports,
    }


def _summary(document: dict) -> dict[str, int]:
    return {
        "entries": len(document.get("entries", [])),
        "nodes": len(document.get("nodes", [])),
        "edges": len(document.get("edges", [])),
        "nets": len(document.get("nets", [])),
        "schedules": len(document.get("schedules", [])),
        "sets": len(document.get("sets", [])),
    }


if __name__ == "__main__":
    raise SystemExit(main())
