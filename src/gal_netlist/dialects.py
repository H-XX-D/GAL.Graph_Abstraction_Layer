"""Dialect registry and validator for GAL:netlist documents."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, Iterable


VOCAB_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
DIALECT_REGISTRY_SCHEMA = "gal.dialects.v0"
DialectSource = Path | Traversable


@dataclass(frozen=True)
class ValidationIssue:
    line: int
    column: int
    code: str
    message: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "message": self.message,
            "text": self.text,
        }


class DialectRegistry:
    def __init__(self, specs: dict[str, dict[str, Any]]):
        self.specs = specs

    def get(self, dialect_id: str | None) -> dict[str, Any] | None:
        if dialect_id is None:
            return None
        return self.specs.get(dialect_id)

    def ids(self) -> list[str]:
        return sorted(self.specs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": DIALECT_REGISTRY_SCHEMA,
            "dialects": {dialect_id: self.specs[dialect_id] for dialect_id in self.ids()},
        }


def load_registry(dialect_dirs: Iterable[DialectSource]) -> DialectRegistry:
    specs: dict[str, dict[str, Any]] = {}
    for directory in dialect_dirs:
        for path in _markdown_specs(directory):
            spec = _load_markdown_spec(path)
            if spec is not None:
                specs[spec["id"]] = spec
    return DialectRegistry(specs)


def default_dialect_dirs(input_path: Path) -> list[DialectSource]:
    """Find local docs/dialects directories plus bundled package defaults."""

    candidates: list[DialectSource] = []
    seen: set[str] = set()
    roots = [Path.cwd(), input_path.resolve().parent]
    for root in roots:
        for parent in [root, *root.parents]:
            candidate = parent / "docs" / "dialects"
            key = str(candidate)
            if key not in seen:
                candidates.append(candidate)
                seen.add(key)
    bundled = files("gal_netlist").joinpath("data", "dialects")
    if str(bundled) not in seen:
        candidates.append(bundled)
    return candidates


def validate_document(document: dict[str, Any], registry: DialectRegistry) -> list[ValidationIssue]:
    dialect_id = document.get("dialect")
    if not dialect_id:
        return []
    spec = registry.get(dialect_id)
    if spec is None:
        return [
            ValidationIssue(
                line=1,
                column=1,
                code="unknown_dialect",
                message=f"dialect {dialect_id!r} is not available in the registry",
                text=f"@dialect {dialect_id}",
            )
        ]

    issues: list[ValidationIssue] = []
    allowed_node_kinds = set(spec.get("nodeKinds", []))
    allowed_relations = set(spec.get("relations", []))
    allowed_fields = set(spec.get("fields", []))
    allowed_signals = set(spec.get("signals", []))
    allowed_net_ops = set(spec.get("netOps", []))
    allowed_standing_ops = set(spec.get("standingOps", []))
    allowed_threads = set(spec.get("threads", []))
    graph_symbols = {node["id"] for node in document.get("nodes", [])}
    graph_symbols.update(net["output"] for net in document.get("nets", []))

    for node in document.get("nodes", []):
        for field in node.get("fields", []):
            if allowed_fields and field["name"] not in allowed_fields:
                issues.append(_issue(node, "unknown_field", f"field {field['name']!r} is not allowed by {dialect_id}"))
        for kind in _node_kinds(node):
            if allowed_node_kinds and kind not in allowed_node_kinds:
                issues.append(_issue(node, "unknown_node_kind", f"node kind {kind!r} is not allowed by {dialect_id}"))

    for edge in document.get("edges", []):
        if allowed_relations and edge["relation"] not in allowed_relations:
            issues.append(_issue(edge, "unknown_relation", f"relation {edge['relation']!r} is not allowed by {dialect_id}"))

    for net in document.get("nets", []):
        if allowed_net_ops and net["op"] not in allowed_net_ops:
            issues.append(_issue(net, "unknown_net_op", f"net op {net['op']!r} is not allowed by {dialect_id}"))
        for signal in net.get("inputs", []):
            if allowed_signals and signal not in allowed_signals and signal not in graph_symbols:
                issues.append(_issue(net, "unknown_signal", f"signal {signal!r} is not allowed by {dialect_id}"))

    for schedule in document.get("schedules", []):
        if allowed_standing_ops and schedule["base"] not in allowed_standing_ops:
            issues.append(
                _issue(schedule, "unknown_standing_op", f"standing op {schedule['base']!r} is not allowed by {dialect_id}")
            )
        if allowed_threads and schedule["thread"] not in allowed_threads:
            issues.append(_issue(schedule, "unknown_thread", f"thread {schedule['thread']!r} is not allowed by {dialect_id}"))

    return issues


def _markdown_specs(directory: DialectSource) -> list[DialectSource]:
    try:
        if not directory.exists() or not directory.is_dir():
            return []
        if isinstance(directory, Path):
            return sorted(directory.glob("*.md"))
        return sorted(
            (child for child in directory.iterdir() if child.is_file() and child.name.endswith(".md")),
            key=lambda child: child.name,
        )
    except OSError:
        return []


def _load_markdown_spec(path: DialectSource) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    match = VOCAB_RE.search(text)
    if not match:
        return None
    spec = json.loads(match.group(1))
    if not isinstance(spec.get("id"), str):
        return None
    return spec


def _node_kinds(node: dict[str, Any]) -> list[str]:
    kinds: list[str] = []
    for param in node.get("params", []):
        if param.get("key") == "kind":
            kinds.extend(str(value) for value in param.get("values", []))
    return kinds


def _issue(entry: dict[str, Any], code: str, message: str) -> ValidationIssue:
    return ValidationIssue(
        line=entry.get("line", 1),
        column=1,
        code=code,
        message=message,
        text=entry.get("source_text") or entry.get("source") or "",
    )
