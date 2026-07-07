"""Canonical renderer for GAL:netlist AST dictionaries."""

from __future__ import annotations

from typing import Any


def render_document(document: dict[str, Any]) -> str:
    """Render parsed GAL AST entries as canonical GAL text."""

    lines: list[str] = []
    current_node: str | None = None
    for entry in document.get("entries", []):
        form = entry["form"]
        if form == "header":
            lines.append(f"@{entry['key']} {entry['value']}")
            current_node = None
        elif form == "node":
            lines.append(_render_node(entry))
            current_node = entry["id"]
        elif form == "body":
            lines.append(f'body "{_escape_string(entry["text"])}"')
        elif form == "edge":
            lines.append(_render_edge(entry, current_node))
        elif form == "net":
            lines.append(f"net {entry['output']} {entry['op']} {' '.join(entry['inputs'])}")
            current_node = None
        elif form == "schedule":
            params = _render_params(entry.get("params", []))
            suffix = f" {params}" if params else ""
            lines.append(f"addf {entry['op']} {entry['thread']}{suffix}")
            current_node = None
        elif form == "set":
            lines.append(f"setp {entry['target']}.{entry['param']} {_render_value(entry['value'])}")
            current_node = None
    return "\n".join(lines) + ("\n" if lines else "")


def _render_node(entry: dict[str, Any]) -> str:
    parts = [entry["id"], f'"{_escape_string(entry["label"])}"']
    for field in entry.get("fields", []):
        parts.append(f"{field['name']}({_render_number(field['value'])})")
    rendered_params = _render_params(entry.get("params", []))
    if rendered_params:
        parts.append(rendered_params)
    return " ".join(parts)


def _render_edge(entry: dict[str, Any], current_node: str | None) -> str:
    arrow = ">" if entry["direction"] == "fwd" else "<"
    edge = f"{entry['relation']}{arrow} {entry['target']}({_render_number(entry['weight'])})"
    if entry.get("attached") and entry["source"] == current_node:
        return edge
    return f"{entry['source']} {edge}"


def _render_params(params: list[dict[str, Any]]) -> str:
    return " ".join(
        f"[{param['key']}: {' '.join(_render_value(value) for value in param.get('values', []))}]"
        for param in params
    )


def _render_value(value: Any) -> str:
    if isinstance(value, str):
        if not value or any(char.isspace() for char in value) or any(char in value for char in '[]"#'):
            return f'"{_escape_string(value)}"'
        return value
    return _render_number(value)


def _render_number(value: Any) -> str:
    if isinstance(value, float):
        text = f"{value:.12g}"
        return "0" if text == "-0" else text
    return str(value)


def _escape_string(value: str) -> str:
    return value.replace("\\", r"\\").replace('"', r"\"").replace("\n", r"\n")
