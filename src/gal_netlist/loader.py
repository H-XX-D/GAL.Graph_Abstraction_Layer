"""In-memory loader for GAL:netlist AST dictionaries."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .dialects import DialectRegistry, validate_document


RUNTIME_SCHEMA = "gal.runtime.v0"
LOAD_MODES = {"verify", "plan", "replay", "merge"}


def load_document(
    document: dict[str, Any],
    *,
    mode: str,
    registry: DialectRegistry | None = None,
    runtime: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Load or inspect a GAL document against an in-memory runtime state."""

    if mode not in LOAD_MODES:
        raise ValueError(f"unsupported load mode {mode!r}")

    working_runtime = _empty_runtime(document) if mode == "replay" else _normalize_runtime(runtime, document)
    report = {
        "ok": True,
        "mode": mode,
        "schema": document.get("schema"),
        "dialect": document.get("dialect"),
        "summary": _summary(document),
        "actions": [],
        "unsupported": [],
        "rejections": [],
    }

    if registry is not None:
        report["rejections"].extend(issue.to_dict() for issue in validate_document(document, registry))

    report["unsupported"].extend(_unsupported_entries(document))

    if report["rejections"] or report["unsupported"]:
        report["ok"] = False
        if mode in {"replay", "merge"}:
            report["runtime"] = working_runtime
        return report

    actions = _planned_actions(document, working_runtime)
    report["actions"] = actions

    if mode == "verify":
        report["matches"] = _matches_runtime(document, working_runtime) if runtime is not None else True
        if not report["matches"]:
            report["ok"] = False
        return report

    if mode == "plan":
        return report

    for action in actions:
        _apply_action(working_runtime, action)
    report["runtime"] = working_runtime
    return report


def _empty_runtime(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "dialect": document.get("dialect"),
        "nodes": {},
        "edges": [],
        "nets": {},
        "schedules": {},
        "sets": [],
    }


def _normalize_runtime(runtime: dict[str, Any] | None, document: dict[str, Any]) -> dict[str, Any]:
    if runtime is None:
        return _empty_runtime(document)
    normalized = deepcopy(runtime)
    normalized.setdefault("schema", RUNTIME_SCHEMA)
    normalized.setdefault("dialect", document.get("dialect"))
    normalized.setdefault("nodes", {})
    normalized.setdefault("edges", [])
    normalized.setdefault("nets", {})
    normalized.setdefault("schedules", {})
    normalized.setdefault("sets", [])
    return normalized


def _summary(document: dict[str, Any]) -> dict[str, int]:
    return {
        "nodes": len(document.get("nodes", [])),
        "edges": len(document.get("edges", [])),
        "nets": len(document.get("nets", [])),
        "schedules": len(document.get("schedules", [])),
        "sets": len(document.get("sets", [])),
    }


def _unsupported_entries(document: dict[str, Any]) -> list[dict[str, Any]]:
    supported = {"header", "node", "body", "edge", "net", "schedule", "set"}
    unsupported = []
    for entry in document.get("entries", []):
        if entry.get("form") not in supported:
            unsupported.append(
                {
                    "line": entry.get("line", 1),
                    "column": 1,
                    "code": "unsupported_form",
                    "message": f"loader does not support form {entry.get('form')!r}",
                    "text": entry.get("source_text") or "",
                }
            )
    return unsupported


def _planned_actions(document: dict[str, Any], runtime: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    runtime_nodes = runtime.get("nodes", {})
    runtime_edges = {_edge_key(edge) for edge in runtime.get("edges", [])}
    runtime_sets = {_set_key(entry) for entry in runtime.get("sets", [])}

    for node in document.get("nodes", []):
        actions.append({"action": "update_node" if node["id"] in runtime_nodes else "create_node", "id": node["id"], "node": node})
    for edge in document.get("edges", []):
        actions.append({"action": "edge_exists" if _edge_key(edge) in runtime_edges else "attach_edge", "edge": edge})
    for net in document.get("nets", []):
        action = "update_net" if net["output"] in runtime.get("nets", {}) else "create_net"
        actions.append({"action": action, "output": net["output"], "net": net})
    for schedule in document.get("schedules", []):
        action = "update_schedule" if schedule["op"] in runtime.get("schedules", {}) else "schedule_op"
        actions.append({"action": action, "op": schedule["op"], "schedule": schedule})
    for entry in document.get("sets", []):
        actions.append({"action": "set_exists" if _set_key(entry) in runtime_sets else "set_param", "set": entry})
    return actions


def _apply_action(runtime: dict[str, Any], action: dict[str, Any]) -> None:
    kind = action["action"]
    if kind in {"create_node", "update_node"}:
        runtime["nodes"][action["id"]] = action["node"]
    elif kind == "attach_edge":
        runtime["edges"].append(action["edge"])
    elif kind in {"create_net", "update_net"}:
        runtime["nets"][action["output"]] = action["net"]
    elif kind in {"schedule_op", "update_schedule"}:
        runtime["schedules"][action["op"]] = action["schedule"]
    elif kind == "set_param":
        runtime["sets"].append(action["set"])


def _matches_runtime(document: dict[str, Any], runtime: dict[str, Any]) -> bool:
    planned = _planned_actions(document, runtime)
    return all(action["action"] in {"update_node", "edge_exists", "update_net", "update_schedule", "set_exists"} for action in planned)


def _edge_key(edge: dict[str, Any]) -> tuple[Any, ...]:
    return (edge.get("source"), edge.get("relation"), edge.get("direction"), edge.get("target"), edge.get("weight"))


def _set_key(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (entry.get("target"), entry.get("param"), entry.get("value"))
