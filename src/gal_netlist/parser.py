"""Parser for the GAL:netlist draft syntax."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


SCHEMA = "gal.netlist.ast.v0"
IDENT = r"[A-Za-z_][A-Za-z0-9_]*"

FIELD_RE = re.compile(rf"^(?P<name>{IDENT})\((?P<value>.*)\)$")
EDGE_RE = re.compile(
    rf"^(?:(?P<source>{IDENT})\s+)?(?P<relation>{IDENT})(?P<dir>[><])\s+"
    rf"(?P<target>{IDENT})\((?P<weight>[-+]?(?:\d+(?:\.\d*)?|\.\d+))\)$"
)
NODE_RE = re.compile(rf"^(?P<id>{IDENT})\s+\"(?P<label>(?:\\.|[^\"])*)\"(?P<rest>.*)$")


@dataclass
class GalParseError(Exception):
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


def parse_text(text: str) -> dict[str, Any]:
    """Parse GAL text into a semantic AST dictionary."""

    document: dict[str, Any] = {
        "schema": SCHEMA,
        "gal": None,
        "dialect": None,
        "entries": [],
        "nodes": [],
        "edges": [],
        "nets": [],
        "schedules": [],
        "sets": [],
        "comments": [],
        "metadata": {},
        "errors": [],
    }
    last_node: str | None = None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        try:
            stripped_comment, comment = _strip_comment(raw_line)
            line = stripped_comment.strip()
            if comment is not None:
                document["comments"].append({"line": line_no, "text": comment})
            if not line:
                continue

            entry = _parse_line(line, line_no, raw_line, last_node)
            document["entries"].append(entry)
            form = entry["form"]
            if form == "header":
                if entry["key"] == "gal":
                    document["gal"] = entry["value"]
                elif entry["key"] == "dialect":
                    document["dialect"] = entry["value"]
                else:
                    document["metadata"][entry["key"]] = entry["value"]
            elif form == "node":
                document["nodes"].append(entry)
                last_node = entry["id"]
            elif form == "body":
                if last_node is None:
                    raise GalParseError(line_no, 1, "body_without_node", "body has no preceding node", raw_line)
                entry["source"] = last_node
            elif form == "edge":
                document["edges"].append(entry)
            elif form == "net":
                document["nets"].append(entry)
            elif form == "schedule":
                document["schedules"].append(entry)
            elif form == "set":
                document["sets"].append(entry)
        except GalParseError as exc:
            document["errors"].append(exc.to_dict())

    return document


def _parse_line(line: str, line_no: int, raw_line: str, last_node: str | None) -> dict[str, Any]:
    if line.startswith("@"):
        return _parse_header(line, line_no, raw_line)
    if line.startswith("body "):
        return _parse_body(line, line_no, raw_line)
    if line.startswith("net "):
        return _parse_net(line, line_no, raw_line)
    if line.startswith("addf "):
        return _parse_schedule(line, line_no, raw_line)
    if line.startswith("setp "):
        return _parse_set(line, line_no, raw_line)

    edge = _parse_edge(line, line_no, raw_line, last_node)
    if edge is not None:
        return edge

    node = _parse_node(line, line_no, raw_line)
    if node is not None:
        return node

    raise GalParseError(line_no, 1, "unknown_form", "line matches no GAL form", raw_line)


def _parse_header(line: str, line_no: int, raw_line: str) -> dict[str, Any]:
    tokens = line.split(None, 1)
    if len(tokens) != 2:
        raise GalParseError(line_no, 1, "bad_header", "header must be @key value", raw_line)
    return {
        "form": "header",
        "key": tokens[0][1:],
        "value": tokens[1].strip(),
        "line": line_no,
        "source_text": raw_line,
    }


def _parse_node(line: str, line_no: int, raw_line: str) -> dict[str, Any] | None:
    match = NODE_RE.match(line)
    if not match:
        return None

    fields: list[dict[str, Any]] = []
    params: list[dict[str, Any]] = []
    for token in _tokenize(match.group("rest").strip(), line_no, raw_line):
        if token.startswith("["):
            params.append(_parse_param(token, line_no, raw_line))
            continue
        field = FIELD_RE.match(token)
        if not field:
            raise GalParseError(line_no, 1, "bad_node_token", f"invalid node token {token!r}", raw_line)
        fields.append({"name": field.group("name"), "value": _parse_scalar(field.group("value"))})

    return {
        "form": "node",
        "id": match.group("id"),
        "label": _unescape_string(match.group("label")),
        "fields": fields,
        "params": params,
        "line": line_no,
        "source_text": raw_line,
    }


def _parse_body(line: str, line_no: int, raw_line: str) -> dict[str, Any]:
    tokens = _tokenize(line, line_no, raw_line)
    if len(tokens) != 2 or not _is_quoted(tokens[1]):
        raise GalParseError(line_no, 1, "bad_body", "body must be body \"text\"", raw_line)
    return {"form": "body", "text": _unescape_string(tokens[1][1:-1]), "line": line_no, "source_text": raw_line}


def _parse_edge(line: str, line_no: int, raw_line: str, last_node: str | None) -> dict[str, Any] | None:
    match = EDGE_RE.match(line)
    if not match:
        return None
    explicit_source = match.group("source")
    if explicit_source is None and last_node is None:
        raise GalParseError(line_no, 1, "edge_without_source", "attached edge has no preceding node", raw_line)
    return {
        "form": "edge",
        "source": explicit_source or last_node,
        "relation": match.group("relation"),
        "direction": "fwd" if match.group("dir") == ">" else "rev",
        "target": match.group("target"),
        "weight": _parse_scalar(match.group("weight")),
        "attached": explicit_source is None,
        "line": line_no,
        "source_text": raw_line,
    }


def _parse_net(line: str, line_no: int, raw_line: str) -> dict[str, Any]:
    tokens = _tokenize(line, line_no, raw_line)
    if len(tokens) < 4:
        raise GalParseError(line_no, 1, "bad_net", "net must be net output op input...", raw_line)
    return {
        "form": "net",
        "output": tokens[1],
        "op": tokens[2],
        "inputs": tokens[3:],
        "line": line_no,
        "source_text": raw_line,
    }


def _parse_schedule(line: str, line_no: int, raw_line: str) -> dict[str, Any]:
    tokens = _tokenize(line, line_no, raw_line)
    if len(tokens) < 3:
        raise GalParseError(line_no, 1, "bad_schedule", "addf must be addf op thread [params...]", raw_line)
    params = [_parse_param(token, line_no, raw_line) for token in tokens[3:]]
    base, instance = _split_instance(tokens[1])
    return {
        "form": "schedule",
        "op": tokens[1],
        "base": base,
        "instance": instance,
        "thread": tokens[2],
        "params": params,
        "line": line_no,
        "source_text": raw_line,
    }


def _parse_set(line: str, line_no: int, raw_line: str) -> dict[str, Any]:
    tokens = _tokenize(line, line_no, raw_line)
    if len(tokens) != 3 or "." not in tokens[1]:
        raise GalParseError(line_no, 1, "bad_set", "setp must be setp target.param value", raw_line)
    target, param = tokens[1].split(".", 1)
    return {
        "form": "set",
        "target": target,
        "param": param,
        "value": _token_value(tokens[2]),
        "line": line_no,
        "source_text": raw_line,
    }


def _strip_comment(line: str) -> tuple[str, str | None]:
    quote = False
    escape = False
    bracket_depth = 0
    for index, char in enumerate(line):
        if escape:
            escape = False
            continue
        if quote and char == "\\":
            escape = True
            continue
        if char == '"':
            quote = not quote
            continue
        if not quote and char == "[":
            bracket_depth += 1
            continue
        if not quote and char == "]" and bracket_depth > 0:
            bracket_depth -= 1
            continue
        if char == "#" and not quote and bracket_depth == 0:
            return line[:index], line[index + 1 :].strip()
    return line, None


def _tokenize(text: str, line_no: int, raw_line: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    quote = False
    escape = False
    bracket_depth = 0

    for char in text:
        if escape:
            current.append(char)
            escape = False
            continue
        if quote and char == "\\":
            current.append(char)
            escape = True
            continue
        if char == '"':
            current.append(char)
            quote = not quote
            continue
        if not quote and char == "[":
            bracket_depth += 1
            current.append(char)
            continue
        if not quote and char == "]":
            bracket_depth -= 1
            current.append(char)
            if bracket_depth < 0:
                raise GalParseError(line_no, 1, "bad_bracket", "unmatched closing bracket", raw_line)
            continue
        if char.isspace() and not quote and bracket_depth == 0:
            if current:
                tokens.append("".join(current))
                current = []
            continue
        current.append(char)

    if quote:
        raise GalParseError(line_no, 1, "bad_string", "unterminated quoted string", raw_line)
    if bracket_depth != 0:
        raise GalParseError(line_no, 1, "bad_bracket", "unterminated bracket parameter", raw_line)
    if current:
        tokens.append("".join(current))
    return tokens


def _parse_param(token: str, line_no: int, raw_line: str) -> dict[str, Any]:
    if not (token.startswith("[") and token.endswith("]")):
        raise GalParseError(line_no, 1, "bad_param", f"expected bracket param, got {token!r}", raw_line)
    body = token[1:-1].strip()
    if ":" not in body:
        raise GalParseError(line_no, 1, "bad_param", "bracket param must be [key: values...]", raw_line)
    key, value_text = body.split(":", 1)
    values = [_token_value(value) for value in _tokenize(value_text.strip(), line_no, raw_line)]
    return {"key": key.strip(), "values": values}


def _split_instance(op: str) -> tuple[str, int | None]:
    match = re.match(r"^(.*?)(\d+)$", op)
    if not match:
        return op, None
    return match.group(1), int(match.group(2))


def _token_value(token: str) -> str:
    if _is_quoted(token):
        return _unescape_string(token[1:-1])
    return token


def _parse_scalar(value: str) -> int | float | str:
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+)", value):
        return float(value)
    return value


def _is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == '"' and value[-1] == '"'


def _unescape_string(value: str) -> str:
    return value.replace(r"\n", "\n").replace(r"\"", '"').replace(r"\\", "\\")
