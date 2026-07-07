"""JSON Schema contracts for GAL CLI payloads."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


SCHEMA_INDEX_SCHEMA = "gal.schemas.v0"


def schema_ids() -> list[str]:
    return sorted(SCHEMAS)


def get_schema(schema_id: str) -> dict[str, Any] | None:
    schema = SCHEMAS.get(schema_id)
    return deepcopy(schema) if schema is not None else None


def schema_index() -> dict[str, Any]:
    return {
        "schema": SCHEMA_INDEX_SCHEMA,
        "schemas": [
            {
                "id": schema_id,
                "title": SCHEMAS[schema_id].get("title", schema_id),
                "description": SCHEMAS[schema_id].get("description", ""),
            }
            for schema_id in schema_ids()
        ],
    }


def write_schemas(output_dir: Path, schema_id: str | None = None) -> list[Path] | None:
    ids = [schema_id] if schema_id else schema_ids()
    if any(item not in SCHEMAS for item in ids):
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if schema_id is None:
        index_path = output_dir / "index.json"
        _write_json(index_path, schema_index())
        written.append(index_path)

    for item in ids:
        path = output_dir / schema_filename(item)
        _write_json(path, get_schema(item))
        written.append(path)
    return written


def schema_filename(schema_id: str) -> str:
    return f"{schema_id}.schema.json"


def _write_json(path: Path, payload: dict[str, Any] | None) -> None:
    if payload is None:
        raise ValueError(f"missing schema for {path}")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


SUMMARY_SCHEMA = {
    "type": "object",
    "required": ["entries", "nodes", "edges", "nets", "schedules", "sets"],
    "properties": {
        "entries": {"type": "integer", "minimum": 0},
        "nodes": {"type": "integer", "minimum": 0},
        "edges": {"type": "integer", "minimum": 0},
        "nets": {"type": "integer", "minimum": 0},
        "schedules": {"type": "integer", "minimum": 0},
        "sets": {"type": "integer", "minimum": 0},
    },
    "additionalProperties": False,
}

CHECKS_SCHEMA = {
    "type": "object",
    "required": ["parse", "semanticRoundtrip", "dialect", "components"],
    "properties": {
        "parse": {"type": "boolean"},
        "semanticRoundtrip": {"type": "boolean"},
        "dialect": {"type": "boolean"},
        "components": {"type": "boolean"},
    },
    "additionalProperties": False,
}

ISSUE_SCHEMA = {
    "type": "object",
    "required": ["line", "column", "code", "message", "text"],
    "properties": {
        "line": {"type": "integer", "minimum": 1},
        "column": {"type": "integer", "minimum": 1},
        "code": {"type": "string"},
        "message": {"type": "string"},
        "text": {"type": "string"},
    },
    "additionalProperties": False,
}

VERIFY_REPORT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "gal.verify_report.v0",
    "title": "GAL verification report",
    "description": "Structured report emitted by gal verify --json.",
    "type": "object",
    "required": ["ok", "path", "schema", "dialect", "summary", "checks", "skipped", "errors", "validation"],
    "properties": {
        "ok": {"type": "boolean"},
        "path": {"type": "string"},
        "schema": {"type": ["string", "null"]},
        "dialect": {"type": ["string", "null"]},
        "summary": SUMMARY_SCHEMA,
        "checks": CHECKS_SCHEMA,
        "skipped": {"type": "array", "items": {"enum": ["dialect", "components"]}},
        "errors": {"type": "array", "items": ISSUE_SCHEMA},
        "validation": {"type": "array", "items": ISSUE_SCHEMA},
        "error": {"type": "string"},
    },
    "additionalProperties": False,
}

VERIFY_BATCH_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "gal.verify_batch.v0",
    "title": "GAL batch verification report",
    "description": "Structured report emitted by gal verify-all --json.",
    "type": "object",
    "required": ["schema", "ok", "count", "passed", "failed", "reports"],
    "properties": {
        "schema": {"const": "gal.verify_batch.v0"},
        "ok": {"type": "boolean"},
        "count": {"type": "integer", "minimum": 0},
        "passed": {"type": "integer", "minimum": 0},
        "failed": {"type": "integer", "minimum": 0},
        "reports": {"type": "array", "items": VERIFY_REPORT_SCHEMA},
    },
    "additionalProperties": False,
}

DIALECT_SPEC_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "string"},
        "nodeKinds": {"type": "array", "items": {"type": "string"}},
        "relations": {"type": "array", "items": {"type": "string"}},
        "fields": {"type": "array", "items": {"type": "string"}},
        "signals": {"type": "array", "items": {"type": "string"}},
        "netOps": {"type": "array", "items": {"type": "string"}},
        "standingOps": {"type": "array", "items": {"type": "string"}},
        "threads": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}

DIALECT_REGISTRY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "gal.dialects.v0",
    "title": "GAL dialect registry",
    "description": "Registry emitted by gal dialects --json.",
    "type": "object",
    "required": ["schema", "dialects"],
    "properties": {
        "schema": {"const": "gal.dialects.v0"},
        "dialects": {"type": "object", "additionalProperties": DIALECT_SPEC_SCHEMA},
    },
    "additionalProperties": False,
}

COMPONENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "gal.components.v0",
    "title": "GAL component registry",
    "description": "Registry emitted by gal components --json.",
    "type": "object",
    "required": ["schema", "netOps", "standingOps"],
    "properties": {
        "schema": {"const": "gal.components.v0"},
        "netOps": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["kind", "name", "arity", "version", "sources"],
                "properties": {
                    "kind": {"const": "net_op"},
                    "name": {"type": "string"},
                    "arity": {"type": ["integer", "null"], "minimum": 0},
                    "version": {"type": "string"},
                    "sources": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
        },
        "standingOps": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["kind", "name", "threads", "threadsBySource", "version", "sources"],
                "properties": {
                    "kind": {"const": "standing_op"},
                    "name": {"type": "string"},
                    "threads": {"type": "array", "items": {"type": "string"}},
                    "threadsBySource": {
                        "type": "object",
                        "additionalProperties": {"type": "array", "items": {"type": "string"}},
                    },
                    "version": {"type": "string"},
                    "sources": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

RUNTIME_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "gal.runtime.v0",
    "title": "GAL in-memory runtime",
    "description": "Runtime shape emitted by gal load --mode replay and merge.",
    "type": "object",
    "required": ["schema", "dialect", "nodes", "edges", "nets", "schedules", "sets"],
    "properties": {
        "schema": {"const": "gal.runtime.v0"},
        "dialect": {"type": ["string", "null"]},
        "nodes": {"type": "object"},
        "edges": {"type": "array"},
        "nets": {"type": "object"},
        "schedules": {"type": "object"},
        "sets": {"type": "array"},
    },
    "additionalProperties": True,
}

AST_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "gal.netlist.ast.v0",
    "title": "GAL netlist AST",
    "description": "Semantic AST emitted by gal parse --json and gal convert --to json.",
    "type": "object",
    "required": ["schema", "gal", "dialect", "entries", "nodes", "edges", "nets", "schedules", "sets", "metadata"],
    "properties": {
        "schema": {"const": "gal.netlist.ast.v0"},
        "gal": {"type": ["string", "null"]},
        "dialect": {"type": ["string", "null"]},
        "entries": {"type": "array"},
        "nodes": {"type": "array"},
        "edges": {"type": "array"},
        "nets": {"type": "array"},
        "schedules": {"type": "array"},
        "sets": {"type": "array"},
        "metadata": {"type": "object"},
    },
    "additionalProperties": True,
}

SCHEMAS = {
    "gal.components.v0": COMPONENT_SCHEMA,
    "gal.dialects.v0": DIALECT_REGISTRY_SCHEMA,
    "gal.netlist.ast.v0": AST_SCHEMA,
    "gal.runtime.v0": RUNTIME_SCHEMA,
    "gal.verify_batch.v0": VERIFY_BATCH_SCHEMA,
    "gal.verify_report.v0": VERIFY_REPORT_SCHEMA,
}
