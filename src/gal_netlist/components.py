"""Component registry for reusable GAL operations."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .dialects import DialectRegistry, ValidationIssue


COMPONENT_SCHEMA = "gal.components.v0"
CORE_NET_ARITY = {
    "not1": 1,
    "and2": 2,
    "or2": 2,
    "xor2": 2,
    "lut5": 5,
}


@dataclass
class NetOpComponent:
    name: str
    arity: int | None = None
    version: str = "0.1.0"
    sources: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "net_op",
            "name": self.name,
            "arity": self.arity,
            "version": self.version,
            "sources": sorted(self.sources),
        }


@dataclass
class StandingOpComponent:
    name: str
    version: str = "0.1.0"
    sources: set[str] = field(default_factory=set)
    threads_by_source: dict[str, set[str]] = field(default_factory=dict)

    def add_source(self, dialect_id: str, threads: set[str]) -> None:
        self.sources.add(dialect_id)
        self.threads_by_source.setdefault(dialect_id, set()).update(threads)

    def threads_for(self, dialect_id: str | None) -> set[str]:
        if dialect_id is not None and dialect_id in self.threads_by_source:
            return set(self.threads_by_source[dialect_id])
        threads: set[str] = set()
        for source_threads in self.threads_by_source.values():
            threads.update(source_threads)
        return threads

    def to_dict(self) -> dict[str, Any]:
        threads = self.threads_for(None)
        return {
            "kind": "standing_op",
            "name": self.name,
            "threads": sorted(threads),
            "threadsBySource": {source: sorted(values) for source, values in sorted(self.threads_by_source.items())},
            "version": self.version,
            "sources": sorted(self.sources),
        }


class ComponentRegistry:
    def __init__(
        self,
        *,
        net_ops: dict[str, NetOpComponent] | None = None,
        standing_ops: dict[str, StandingOpComponent] | None = None,
    ):
        self.net_ops = net_ops or {}
        self.standing_ops = standing_ops or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": COMPONENT_SCHEMA,
            "netOps": {name: component.to_dict() for name, component in sorted(self.net_ops.items())},
            "standingOps": {name: component.to_dict() for name, component in sorted(self.standing_ops.items())},
        }


def build_component_registry(dialect_registry: DialectRegistry) -> ComponentRegistry:
    net_ops: dict[str, NetOpComponent] = {}
    standing_ops: dict[str, StandingOpComponent] = {}

    for dialect_id in dialect_registry.ids():
        spec = dialect_registry.get(dialect_id)
        if spec is None:
            continue

        for op in spec.get("netOps", []):
            component = net_ops.setdefault(op, NetOpComponent(name=op, arity=_net_arity(op)))
            component.sources.add(dialect_id)

        threads = set(spec.get("threads", []))
        for op in spec.get("standingOps", []):
            standing_ops.setdefault(op, StandingOpComponent(name=op)).add_source(dialect_id, threads)

    return ComponentRegistry(net_ops=net_ops, standing_ops=standing_ops)


def validate_components(document: dict[str, Any], registry: ComponentRegistry) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    dialect_id = document.get("dialect")

    for net in document.get("nets", []):
        op = net["op"]
        component = registry.net_ops.get(op)
        if component is None:
            issues.append(_issue(net, "unknown_component", f"net component {op!r} is not registered"))
            continue
        if component.arity is not None and len(net.get("inputs", [])) != component.arity:
            issues.append(
                _issue(
                    net,
                    "wrong_arity",
                    f"net component {op!r} expects {component.arity} input(s), got {len(net.get('inputs', []))}",
                )
            )

    for schedule in document.get("schedules", []):
        op = schedule["base"]
        component = registry.standing_ops.get(op)
        if component is None:
            issues.append(_issue(schedule, "unknown_component", f"standing component {op!r} is not registered"))
            continue
        allowed_threads = component.threads_for(dialect_id)
        if allowed_threads and schedule["thread"] not in allowed_threads:
            issues.append(
                _issue(
                    schedule,
                    "unsupported_thread",
                    f"standing component {op!r} does not support thread {schedule['thread']!r}",
                )
            )

    return issues


def _net_arity(op: str) -> int | None:
    if op in CORE_NET_ARITY:
        return CORE_NET_ARITY[op]
    match = re.search(r"(\d+)$", op)
    return int(match.group(1)) if match else None


def _issue(entry: dict[str, Any], code: str, message: str) -> ValidationIssue:
    return ValidationIssue(
        line=entry.get("line", 1),
        column=1,
        code=code,
        message=message,
        text=entry.get("source_text") or entry.get("source") or "",
    )
