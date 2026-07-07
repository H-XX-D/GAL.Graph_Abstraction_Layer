"""Bundled GAL example discovery and export helpers."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Iterable

from .parser import parse_text


EXAMPLE_REGISTRY_SCHEMA = "gal.examples.v0"


@dataclass(frozen=True)
class ExampleFile:
    name: str
    dialect: str | None
    resource: Traversable

    def read_text(self) -> str:
        return self.resource.read_text(encoding="utf-8")

    def to_dict(self) -> dict[str, str | None]:
        return {"name": self.name, "dialect": self.dialect}


def bundled_examples() -> list[ExampleFile]:
    root = files("gal_netlist").joinpath("data", "examples")
    return sorted(_walk_examples(root, ""), key=lambda item: item.name)


def example_registry(examples: Iterable[ExampleFile] | None = None) -> dict:
    items = list(examples) if examples is not None else bundled_examples()
    return {"schema": EXAMPLE_REGISTRY_SCHEMA, "examples": [item.to_dict() for item in items]}


def find_example(name: str) -> ExampleFile | None:
    for example in bundled_examples():
        if example.name == name:
            return example
    return None


def write_examples(output_dir: Path, examples: Iterable[ExampleFile], *, force: bool = False) -> list[Path]:
    written: list[Path] = []
    for example in examples:
        target = output_dir / example.name
        if target.exists() and not force:
            raise FileExistsError(str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(example.read_text(), encoding="utf-8")
        written.append(target)
    return written


def _walk_examples(directory: Traversable, prefix: str) -> list[ExampleFile]:
    if not directory.exists() or not directory.is_dir():
        return []
    examples: list[ExampleFile] = []
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        name = f"{prefix}{child.name}"
        if child.is_dir():
            examples.extend(_walk_examples(child, f"{name}/"))
        elif child.is_file() and child.name.endswith(".gal"):
            examples.append(ExampleFile(name=name, dialect=_read_dialect(child), resource=child))
    return examples


def _read_dialect(resource: Traversable) -> str | None:
    document = parse_text(resource.read_text(encoding="utf-8"))
    if document.get("errors"):
        return None
    dialect = document.get("dialect")
    return dialect if isinstance(dialect, str) else None
