"""Command line interface for GAL:netlist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ._version import __version__
from .components import build_component_registry, validate_components
from .converters import to_cypher, to_dot, to_yaml
from .dialects import default_dialect_dirs, load_registry, validate_document
from .loader import LOAD_MODES, load_document
from .parser import parse_text
from .renderer import render_document
from .schemas import get_schema, schema_filename, schema_ids, schema_index, write_schemas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gal")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser("parse", help="parse GAL text")
    parse_cmd.add_argument("path", type=Path)
    parse_cmd.add_argument("--json", action="store_true", help="emit JSON AST")

    format_cmd = subparsers.add_parser("format", help="render canonical GAL text")
    format_cmd.add_argument("path", type=Path)

    init_cmd = subparsers.add_parser("init", help="create a starter GAL file")
    init_cmd.add_argument("path", type=Path)
    init_cmd.add_argument("--dialect", default="mal.v0", help="dialect id for the starter file")
    init_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")
    init_cmd.add_argument("--force", action="store_true", help="overwrite an existing file")
    init_cmd.add_argument("--parents", action="store_true", help="create parent directories")
    init_cmd.add_argument("--json", action="store_true", help="emit JSON init report")

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

    schemas_cmd = subparsers.add_parser("schemas", help="list or emit JSON Schema contracts")
    schemas_cmd.add_argument("schema_id", nargs="?", help="schema id to emit")
    schemas_cmd.add_argument("--json", action="store_true", help="emit JSON schema index")
    schemas_cmd.add_argument("--write-dir", type=Path, help="write schema JSON files into a directory")

    doctor_cmd = subparsers.add_parser("doctor", help="report GAL CLI diagnostics")
    doctor_cmd.add_argument("--dialect-dir", type=Path, action="append", help="directory containing dialect markdown specs")
    doctor_cmd.add_argument("--json", action="store_true", help="emit JSON diagnostic report")

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

    if args.command == "schemas":
        if args.write_dir:
            written = write_schemas(args.write_dir, args.schema_id)
            if written is None:
                print(json.dumps({"ok": False, "error": "unknown_schema", "schema": args.schema_id}, indent=2), file=sys.stderr)
                return 1
            for path in written:
                print(path)
            return 0
        if args.schema_id:
            schema = get_schema(args.schema_id)
            if schema is None:
                print(json.dumps({"ok": False, "error": "unknown_schema", "schema": args.schema_id}, indent=2), file=sys.stderr)
                return 1
            print(json.dumps(schema, indent=2, sort_keys=True))
            return 0
        if args.json:
            print(json.dumps(schema_index(), indent=2, sort_keys=True))
            return 0
        for schema_id in schema_ids():
            print(schema_id)
        return 0

    if args.command == "doctor":
        report = _doctor_report(args.dialect_dir or default_dialect_dirs(Path.cwd()))
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"version: {report['version']}")
            print(f"python: {report['python']}")
            print(f"cwd: {report['cwd']}")
            print(f"dialects: {report['dialectCount']}")
            print(f"schemas: {report['schemaCount']}")
            print(f"docs schemas complete: {'yes' if report['docsSchemas']['complete'] else 'no'}")
        return 0

    if args.command == "init":
        registry = load_registry(args.dialect_dir or default_dialect_dirs(args.path))
        spec = registry.get(args.dialect)
        if spec is None:
            report = _init_report(
                ok=False,
                path=args.path,
                dialect=args.dialect,
                created=False,
                overwritten=False,
                node=None,
                error="unknown_dialect",
            )
            _print_init_report(report, args.json)
            return 1
        if args.path.exists() and not args.force:
            report = _init_report(
                ok=False,
                path=args.path,
                dialect=args.dialect,
                created=False,
                overwritten=False,
                node=None,
                error="file_exists",
            )
            _print_init_report(report, args.json)
            return 1
        overwritten = args.path.exists()
        if args.parents:
            args.path.parent.mkdir(parents=True, exist_ok=True)
        node = _starter_node(spec)
        try:
            args.path.write_text(_starter_text(args.dialect, node), encoding="utf-8")
        except OSError as exc:
            report = _init_report(
                ok=False,
                path=args.path,
                dialect=args.dialect,
                created=False,
                overwritten=overwritten,
                node=node,
                error="write_error",
                message=str(exc),
            )
            _print_init_report(report, args.json)
            return 1
        report = _init_report(
            ok=True,
            path=args.path,
            dialect=args.dialect,
            created=True,
            overwritten=overwritten,
            node=node,
        )
        _print_init_report(report, args.json)
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


def _doctor_report(dialect_dirs: list[Path]) -> dict:
    registry = load_registry(dialect_dirs)
    docs_schemas_dir = _find_docs_schemas_dir()
    files = {schema_filename(schema_id): False for schema_id in schema_ids()}
    index_exists = False
    if docs_schemas_dir is not None:
        index_exists = (docs_schemas_dir / "index.json").exists()
        files = {filename: (docs_schemas_dir / filename).exists() for filename in files}
    docs_complete = index_exists and all(files.values())
    dialect_ids = registry.ids()
    schema_id_list = schema_ids()

    return {
        "schema": "gal.doctor.v0",
        "ok": True,
        "version": __version__,
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
        "dialectDirs": [str(path) for path in dialect_dirs],
        "dialectCount": len(dialect_ids),
        "dialects": dialect_ids,
        "schemaCount": len(schema_id_list),
        "schemas": schema_id_list,
        "docsSchemas": {
            "path": str(docs_schemas_dir) if docs_schemas_dir is not None else None,
            "index": index_exists,
            "files": files,
            "complete": docs_complete,
        },
        "checks": {
            "dialectsLoaded": bool(dialect_ids),
            "schemasRegistered": bool(schema_id_list),
            "docsSchemasComplete": docs_complete,
        },
    }


def _find_docs_schemas_dir() -> Path | None:
    for root in [Path.cwd(), *Path.cwd().parents]:
        candidate = root / "docs" / "schemas"
        if candidate.exists():
            return candidate
    return None


def _print_init_report(report: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif report["ok"]:
        print(f"created: {report['path']}")
    else:
        payload = {"ok": False, "error": report["error"]}
        if report["error"] == "unknown_dialect":
            payload["dialect"] = report["dialect"]
        else:
            payload["path"] = report["path"]
        if report.get("message"):
            payload["message"] = report["message"]
        print(json.dumps(payload, indent=2), file=sys.stderr)


def _init_report(
    *,
    ok: bool,
    path: Path,
    dialect: str,
    created: bool,
    overwritten: bool,
    node: dict | None,
    error: str | None = None,
    message: str | None = None,
) -> dict:
    return {
        "schema": "gal.init_report.v0",
        "ok": ok,
        "path": str(path),
        "dialect": dialect,
        "created": created,
        "overwritten": overwritten,
        "node": node,
        "error": error,
        "message": message,
    }


def _starter_node(spec: dict) -> dict:
    node_kinds = spec.get("nodeKinds") or ["node"]
    kind = str(node_kinds[0])
    node_id = f"{_safe_identifier(kind)}_1"
    label = f"Starter {kind.replace('_', ' ')}"
    return {"id": node_id, "kind": kind, "label": label}


def _starter_text(dialect_id: str, node: dict) -> str:
    return f'@gal netlist.v0\n@dialect {dialect_id}\n\n{node["id"]} "{node["label"]}" [kind: {node["kind"]}]\n'


def _safe_identifier(value: str) -> str:
    chars = [char if char.isalnum() or char == "_" else "_" for char in value.lower()]
    identifier = "".join(chars).strip("_") or "node"
    if identifier[0].isdigit():
        return f"n_{identifier}"
    return identifier


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
