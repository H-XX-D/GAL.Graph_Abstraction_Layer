"""Conversion helpers for GAL:netlist AST dictionaries."""

from __future__ import annotations

import re
from typing import Any


def to_dot(document: dict[str, Any]) -> str:
    """Render a parsed GAL document as Graphviz DOT."""

    lines = ["digraph G {"]
    declared_nodes: set[str] = set()

    for node in document.get("nodes", []):
        declared_nodes.add(node["id"])
        attrs = {"label": node["label"], "_gal_form": "node"}
        for field in node.get("fields", []):
            attrs[f"_gal_{field['name']}"] = str(field["value"])
        for param in node.get("params", []):
            attrs[f"_gal_param_{param['key']}"] = " ".join(str(value) for value in param.get("values", []))
        lines.append(f"  {node['id']} [{_dot_attrs(attrs)}];")

    for edge in document.get("edges", []):
        if edge["source"] not in declared_nodes:
            lines.append(f"  {edge['source']} [label={_dot_quote(edge['source'])}, _gal_form=\"implicit_node\"];")
            declared_nodes.add(edge["source"])
        if edge["target"] not in declared_nodes:
            lines.append(f"  {edge['target']} [label={_dot_quote(edge['target'])}, _gal_form=\"implicit_node\"];")
            declared_nodes.add(edge["target"])
        attrs = {
            "label": f"{edge['relation']} {edge['weight']}",
            "_gal_relation": edge["relation"],
            "_gal_weight": str(edge["weight"]),
        }
        if edge["direction"] == "fwd":
            lines.append(f"  {edge['source']} -> {edge['target']} [{_dot_attrs(attrs)}];")
        else:
            lines.append(f"  {edge['target']} -> {edge['source']} [{_dot_attrs(attrs)}];")

    for net in document.get("nets", []):
        net_id = _dot_id(f"gal_net_{net['output']}")
        attrs = {"shape": "box", "label": f"net {net['output']} {net['op']}", "_gal_form": "net"}
        lines.append(f"  {net_id} [{_dot_attrs(attrs)}];")
        for input_id in net.get("inputs", []):
            lines.append(f"  {input_id} -> {net_id} [{_dot_attrs({'label': 'input'})}];")
        lines.append(f"  {net_id} -> {net['output']} [{_dot_attrs({'label': 'output'})}];")

    for schedule in document.get("schedules", []):
        schedule_id = _dot_id(f"gal_schedule_{schedule['op']}")
        attrs = {
            "shape": "box",
            "label": f"{schedule['op']} {schedule['thread']}",
            "_gal_form": "schedule",
            "_gal_base": str(schedule.get("base")),
            "_gal_thread": schedule["thread"],
        }
        lines.append(f"  {schedule_id} [{_dot_attrs(attrs)}];")

    for entry in document.get("sets", []):
        set_id = _dot_id(f"gal_set_{entry['target']}_{entry['param']}")
        attrs = {
            "shape": "note",
            "label": f"setp {entry['target']}.{entry['param']} {entry['value']}",
            "_gal_form": "set",
        }
        lines.append(f"  {set_id} [{_dot_attrs(attrs)}];")
        lines.append(f"  {set_id} -> {entry['target']} [{_dot_attrs({'style': 'dotted', 'label': 'sets'})}];")

    lines.append("}")
    return "\n".join(lines) + "\n"


def to_yaml(value: Any) -> str:
    """Render a JSON-like value as simple block YAML without external deps."""

    return _yaml_value(value, 0).rstrip() + "\n"


def to_cypher(document: dict[str, Any]) -> str:
    """Render a parsed GAL document as Cypher import statements."""

    lines = [
        "CREATE CONSTRAINT gal_node_id IF NOT EXISTS FOR (n:GalNode) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT gal_net_id IF NOT EXISTS FOR (n:GalNet) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT gal_schedule_id IF NOT EXISTS FOR (n:GalSchedule) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT gal_set_id IF NOT EXISTS FOR (n:GalSet) REQUIRE n.id IS UNIQUE;",
    ]
    declared_nodes: set[str] = set()

    for node in document.get("nodes", []):
        declared_nodes.add(node["id"])
        props = {
            "id": node["id"],
            "label": node["label"],
            "gal_form": "node",
            "fields": {field["name"]: field["value"] for field in node.get("fields", [])},
            "params": {param["key"]: param.get("values", []) for param in node.get("params", [])},
        }
        lines.append(f"MERGE (n:GalNode {{id: {_cypher_value(node['id'])}}}) SET n += {_cypher_map(props)};")

    for edge in document.get("edges", []):
        _ensure_cypher_node(lines, declared_nodes, edge["source"])
        _ensure_cypher_node(lines, declared_nodes, edge["target"])
        relation = _cypher_rel_type(edge["relation"])
        props = {"relation": edge["relation"], "weight": edge["weight"], "direction": edge["direction"]}
        if edge["direction"] == "fwd":
            lines.append(
                f"MATCH (s:GalNode {{id: {_cypher_value(edge['source'])}}}), (t:GalNode {{id: {_cypher_value(edge['target'])}}}) "
                f"MERGE (s)-[r:{relation}]->(t) SET r += {_cypher_map(props)};"
            )
        else:
            lines.append(
                f"MATCH (s:GalNode {{id: {_cypher_value(edge['source'])}}}), (t:GalNode {{id: {_cypher_value(edge['target'])}}}) "
                f"MERGE (t)-[r:{relation}]->(s) SET r += {_cypher_map(props)};"
            )

    for net in document.get("nets", []):
        net_id = f"net:{net['output']}"
        props = {"id": net_id, "output": net["output"], "op": net["op"], "inputs": net.get("inputs", []), "gal_form": "net"}
        lines.append(f"MERGE (n:GalNet {{id: {_cypher_value(net_id)}}}) SET n += {_cypher_map(props)};")
        for input_id in net.get("inputs", []):
            _ensure_cypher_node(lines, declared_nodes, input_id)
            lines.append(
                f"MATCH (i:GalNode {{id: {_cypher_value(input_id)}}}), (n:GalNet {{id: {_cypher_value(net_id)}}}) "
                "MERGE (i)-[:GAL_NET_INPUT]->(n);"
            )
        _ensure_cypher_node(lines, declared_nodes, net["output"])
        lines.append(
            f"MATCH (n:GalNet {{id: {_cypher_value(net_id)}}}), (o:GalNode {{id: {_cypher_value(net['output'])}}}) "
            "MERGE (n)-[:GAL_NET_OUTPUT]->(o);"
        )

    for schedule in document.get("schedules", []):
        schedule_id = f"schedule:{schedule['op']}"
        props = {
            "id": schedule_id,
            "op": schedule["op"],
            "base": schedule.get("base"),
            "instance": schedule.get("instance"),
            "thread": schedule["thread"],
            "params": {param["key"]: param.get("values", []) for param in schedule.get("params", [])},
            "gal_form": "schedule",
        }
        lines.append(f"MERGE (s:GalSchedule {{id: {_cypher_value(schedule_id)}}}) SET s += {_cypher_map(props)};")

    for entry in document.get("sets", []):
        set_id = f"set:{entry['target']}:{entry['param']}"
        props = {
            "id": set_id,
            "target": entry["target"],
            "param": entry["param"],
            "value": entry["value"],
            "gal_form": "set",
        }
        lines.append(f"MERGE (s:GalSet {{id: {_cypher_value(set_id)}}}) SET s += {_cypher_map(props)};")
        _ensure_cypher_node(lines, declared_nodes, entry["target"])
        lines.append(
            f"MATCH (s:GalSet {{id: {_cypher_value(set_id)}}}), (t:GalNode {{id: {_cypher_value(entry['target'])}}}) "
            "MERGE (s)-[:GAL_SETS]->(t);"
        )

    return "\n".join(lines) + "\n"


def _yaml_value(value: Any, indent: int) -> str:
    prefix = " " * indent
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{prefix}{key}:")
                lines.append(_yaml_value(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return "[]"
        lines = []
        for item in value:
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{prefix}-")
                lines.append(_yaml_value(item, indent + 2))
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{prefix}{_yaml_scalar(value)}"


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or any(char.isspace() for char in text) or any(char in text for char in ':[]{}#&*!|>\'"%@`'):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return text


def _dot_attrs(attrs: dict[str, str]) -> str:
    return ", ".join(f"{key}={_dot_quote(value)}" for key, value in attrs.items())


def _dot_quote(value: str) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _dot_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def _ensure_cypher_node(lines: list[str], declared_nodes: set[str], node_id: str) -> None:
    if node_id in declared_nodes:
        return
    declared_nodes.add(node_id)
    props = {"id": node_id, "label": node_id, "gal_form": "implicit_node"}
    lines.append(f"MERGE (n:GalNode {{id: {_cypher_value(node_id)}}}) SET n += {_cypher_map(props)};")


def _cypher_rel_type(value: str) -> str:
    rel = re.sub(r"[^A-Za-z0-9_]", "_", value).upper()
    if not rel or rel[0].isdigit():
        return f"GAL_REL_{rel}"
    return rel


def _cypher_map(mapping: dict[str, Any]) -> str:
    items = ", ".join(f"{key}: {_cypher_value(value)}" for key, value in mapping.items() if value is not None)
    return "{" + items + "}"


def _cypher_value(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_cypher_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return _cypher_map(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"
