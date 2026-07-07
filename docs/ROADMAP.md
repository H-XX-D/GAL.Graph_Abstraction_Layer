# GAL Roadmap

This roadmap turns the current GAL:netlist draft into a usable interchange
format and implementation surface.

## Phase 0: Definition

- Freeze the canonical AST object names and required fields.
- Decide whether compact node lines stay as `<id> "label"` or become explicit
  `node <id> "label"`.
- Decide whether `@gal` and `@dialect` remain the header syntax.
- Define the first dialect schema for `mal.v0`.
- Draft the initial dialect schemas for `dal.v0`, `pal.v0`, `aal.v0`,
  `wal.v0`, and `oal.v0`.
- Expand the dialect family with resource, state, event, capability, interface,
  topology, quality, failure, knowledge, reasoning, learning, governance, risk,
  audit, and verification dialects.
- Add fixtures that exercise every line form.

## Phase 1: Parser And Renderer

- Implement a tokenizer that respects quoted strings, bracket parameters, and
  trailing comments.
- Parse every line into typed AST entries with line and column diagnostics.
- Return structured errors without executing operations.
- Render canonical GAL from AST.
- Add semantic round-trip tests:

```text
GAL text -> AST -> canonical GAL text -> AST
```

## Phase 2: Dialect Validation

- Load dialect schemas from local JSON files.
- Validate node kinds, edge relations, fields, signals, operations, and threads.
- Preserve unknown bracket parameters when the selected dialect permits them.
- Reject unknown line forms with actionable diagnostics.

## Phase 3: Conversion

- Convert GAL text to JSON AST.
- Convert JSON AST to canonical GAL text.
- Export DOT for visualization.
- Export YAML for configuration exchange.
- Prototype Cypher export for graph database import.

## Phase 4: Runtime Integration

- Define loader modes: `verify`, `plan`, `merge`, and `replay`.
- Add loader reporting for admitted nodes, attached edges, created nets,
  scheduled operations, parameter sets, and rejections.
- Define a component registry for net operations and standing operations.

## Near-Term Deliverable

The first useful release should include:

- `gal parse`
- `gal format`
- `gal verify`
- Round-trip fixtures
- `mal.v0` dialect validation
