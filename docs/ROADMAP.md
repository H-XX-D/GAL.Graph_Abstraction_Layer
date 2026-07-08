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
  audit, verification, and hardware dialects.
- Add fixtures that exercise every line form.

## Phase 1: Parser And Renderer

Status: initial implementation landed. The current Python package parses the
checked-in GAL examples, renders canonical GAL text, and verifies semantic
round-trips.

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

Status: initial implementation landed. `gal verify` now loads dialect vocabulary
blocks from `docs/dialects/*.md` and validates node kinds, fields, relations,
signals, net operations, standing operations, and threads.
`gal dialects --json` exports the loaded registry as machine-readable data.
`gal verify --json` emits a structured verification report for CI and adapters.
`gal verify-all` verifies files or directories and can emit a batch JSON report.

- Load dialect schemas from local markdown JSON vocabulary blocks.
- Validate node kinds, edge relations, fields, signals, operations, and threads.
- Preserve unknown bracket parameters when the selected dialect permits them.
- Reject unknown line forms with actionable diagnostics.

## Phase 3: Conversion

Status: initial JSON, DOT, YAML, and Cypher export support landed. Conversion
routes GAL text through the parsed semantic AST, and JSON AST can render back to
canonical GAL text.

- Convert GAL text to JSON AST.
- Export DOT for visualization.
- Export YAML for configuration exchange.
- Convert JSON AST to canonical GAL text.
- Prototype Cypher export for graph database import.

## Phase 4: Runtime Integration

Status: initial in-memory loader contract and component registry landed.
`gal load` supports `verify`, `plan`, `replay`, and `merge` modes and returns
structured JSON reports before any external runtime adapter is introduced.
`gal components` exports reusable net-operation and standing-operation metadata
derived from the loaded dialect vocabularies.

- Define loader modes: `verify`, `plan`, `merge`, and `replay`.
- Add loader reporting for admitted nodes, attached edges, created nets,
  scheduled operations, parameter sets, and rejections.
- Define a component registry for net operations and standing operations.
- Validate component arity and supported standing-operation threads during
  verify and load.

## Phase 5: Project Automation

Status: initial CI workflow landed. GitHub Actions runs unit tests, batch
fixture verification, package build verification, and CLI smoke checks on push
and pull request.
`gal schemas` exposes JSON Schema contracts for CLI payloads and runtime data.
Static schema files are published under `docs/schemas/`.
`gal --version` reports the installed CLI version for diagnostics.
`gal doctor` reports version, runtime, dialect, schema, and docs-schema health.
`gal init` creates starter GAL files from the registered dialect vocabulary and
can emit structured JSON reports.
`gal examples` exposes package-bundled examples for installed CLI users and can
filter them by dialect.

- Run `python -m pytest -q` in CI.
- Build the source distribution and wheel in CI.
- Smoke-test the built wheel from a temporary install outside the checkout.
- Run `gal verify-all examples --json` in CI.
- Smoke registry, conversion, and loader CLI commands in CI.
- Publish schema contracts for adapter-facing JSON payloads.
- Validate representative CLI payloads against the published JSON Schemas.
- Keep checked-in static schema files synchronized with the in-code registry.
- Expose the package version through the CLI and Python package.
- Add a doctor command for local and adapter diagnostics.
- Add a starter-file generator for registered dialects.
- Bundle examples and expose them through the CLI.

## Release Readiness

The repository has enough implemented surface for a first `0.1.0` release
candidate. Before tagging or publishing a package, finish these decisions and
checks:

- Decide whether `0.1.0` is a source-only GitHub release, a PyPI package
  release, or both.
- Decide whether the package should remain named `gal-netlist` or reserve a
  broader distribution name before the first public package publish.
- Confirm the public README language, especially the draft status and dialect
  stability expectations.
- Confirm that `GAL_NETLIST_SPEC.md`, `docs/dialects/*.md`, and bundled
  examples describe the same syntax and validation behavior.
- Add release instructions for building, verifying, tagging, and publishing the
  package.
- Tag the release only after local tests, package build, installed-wheel smoke
  tests, CI, and Pages deployment are green for the exact commit.

The next engineering increment is release automation:
`scripts/release_check.py` runs the local release gate in one place and prints
the tag/publish commands without performing destructive actions.
