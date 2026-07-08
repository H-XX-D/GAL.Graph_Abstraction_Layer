# GAL.Graph_Abstraction_Layer

[![CI](https://github.com/H-XX-D/GAL.Graph_Abstraction_Layer/actions/workflows/ci.yml/badge.svg)](https://github.com/H-XX-D/GAL.Graph_Abstraction_Layer/actions/workflows/ci.yml)
[![Docs](https://github.com/H-XX-D/GAL.Graph_Abstraction_Layer/actions/workflows/pages.yml/badge.svg)](https://github.com/H-XX-D/GAL.Graph_Abstraction_Layer/actions/workflows/pages.yml)

Graph Abstraction Layer (GAL) is a small, inspectable interchange layer for
graph-runtime state: nodes, edges, signal wiring, standing operations, runtime
parameter changes, and domain-specific validation vocabularies.

The first concrete syntax profile is `GAL:netlist`, a line-oriented format
designed for semantic round trips and adapter-friendly tooling. Dialects such as
MAL, HAL, DAL, PAL, and VAL all use the same syntax while specializing the
allowed vocabulary for a runtime domain.

## Current Status

Status: draft v0.1.

The repository currently includes a Python CLI, parser, canonical renderer,
semantic round-trip verification, JSON/DOT/YAML/Cypher converters, runtime load
reports, bundled examples, JSON Schema contracts, GitHub Actions CI, and static
GitHub Pages documentation.

## Quickstart

Install locally:

```bash
python3 -m pip install -e ".[dev]"
```

Verify the package and examples:

```bash
python3 -m pytest -q
gal verify-all examples --json
gal dialects
gal examples
```

Create and verify a starter graph:

```bash
gal init starter.hal.gal --dialect hal.v0
gal verify starter.hal.gal
gal convert starter.hal.gal --to dot
```

## Repository Map

- [GAL_NETLIST_SPEC.md](GAL_NETLIST_SPEC.md): draft GAL:netlist specification.
- [docs/ROADMAP.md](docs/ROADMAP.md): implementation and refinement milestones.
- [docs/GLOSSARY.md](docs/GLOSSARY.md): working terms and vocabulary.
- [docs/dialects/](docs/dialects/): draft GAL dialect specifications.
- [docs/schemas/](docs/schemas/): JSON Schema contracts for CLI payloads.
- [docs/blog/](docs/blog/): draft launch and design posts with generated
  image assets.
- [examples/minimal.mal.gal](examples/minimal.mal.gal): minimal MAL dialect
  example using GAL:netlist syntax.
- [examples/dialects/](examples/dialects/): minimal examples for draft dialects.
- [docs/index.html](docs/index.html): static project page deployed with GitHub
  Pages.

## Core Contract

GAL text should round-trip through a canonical AST:

```text
GAL text -> AST -> canonical GAL text -> AST
```

The second AST must be semantically equivalent to the first. Formatting,
comments, and whitespace can be handled by a richer editor layer, but the core
interchange guarantee is semantic preservation.

## Implemented Surface

- Parser support for headers, dialect declarations, nodes, bodies, edges, nets,
  schedules, parameter sets, and comments.
- Canonical rendering and semantic round-trip verification.
- Dialect registry loaded from Markdown vocabulary blocks.
- Bundled dialect and example assets available after wheel install.
- JSON, DOT, YAML, and Cypher conversion commands.
- In-memory load reports for `verify`, `plan`, `replay`, and `merge` modes.
- JSON Schema publishing for CLI payloads and adapter contracts.

## Draft Dialects

GAL dialects share the GAL:netlist syntax and specialize validation vocabulary:

| dialect | name | domain |
|---|---|---|
| `aal.v0` | Agent Abstraction Layer | agents, tools, tasks, handoffs |
| `audal.v0` | Audit Abstraction Layer | evidence, attestations, receipts, trails |
| `cal.v0` | Capability Abstraction Layer | permissions, tools, grants, negotiation |
| `dal.v0` | Deployment Abstraction Layer | services, releases, rollout state |
| `eal.v0` | Event Abstraction Layer | events, streams, triggers, replay |
| `fal.v0` | Failure Abstraction Layer | failures, blast radius, recovery paths |
| `goval.v0` | Governance Abstraction Layer | ownership, authority, lifecycle, escalation |
| `hal.v0` | Hardware Abstraction Layer | devices, buses, drivers, firmware, capabilities |
| `ial.v0` | Interface Abstraction Layer | APIs, contracts, schemas, protocols |
| `kal.v0` | Knowledge Abstraction Layer | concepts, sources, provenance |
| `lal.v0` | Learning Abstraction Layer | examples, feedback, evaluations, preference updates |
| `mal.v0` | Memory Abstraction Language | claims, evidence, memory programs |
| `oal.v0` | Observability Abstraction Layer | signals, alerts, traces, monitors |
| `pal.v0` | Policy Abstraction Layer | rules, obligations, decisions |
| `qal.v0` | Quality Abstraction Layer | SLOs, guarantees, constraints, correctness |
| `ral.v0` | Resource Abstraction Layer | compute, storage, network, quota |
| `real.v0` | Reasoning Abstraction Layer | hypotheses, plans, critiques, decisions |
| `riskal.v0` | Risk Abstraction Layer | risks, controls, mitigations, acceptance |
| `sal.v0` | State Abstraction Layer | state, snapshots, migrations, consistency |
| `tal.v0` | Topology Abstraction Layer | regions, clusters, routes, placement |
| `val.v0` | Verification Abstraction Layer | tests, checks, proofs, acceptance criteria |
| `wal.v0` | Workflow Abstraction Layer | steps, jobs, gates, retries |

These dialects are optional lenses over graph state. A runtime should load only
the dialects it needs, and cross-dialect edges should stay explicit. Each
registered dialect has a Markdown vocabulary and at least one example under
`examples/dialects/`.

## Draft Blog Posts

- [The GAL Dialect Library](docs/blog/2026-07-07-gal-dialect-library.md)
- [HAL as a Boundary Discipline for Graph Runtimes](docs/blog/2026-07-07-hal-boundary-discipline.md)
- [MAL and Durable Memory Graphs](docs/blog/2026-07-07-mal-memory-graphs.md)

## Development Notes

Install the local CLI in editable mode:

```bash
python3 -m pip install -e ".[dev]"
```

Run the current checks:

```bash
python3 -m pytest -q
python3 -m build
gal --version
gal doctor --json
gal examples
gal examples --json
gal examples --name minimal.mal.gal
gal examples --write-dir /tmp/gal-examples
gal init starter.mal.gal
gal init starter.hal.gal --dialect hal.v0 --json
gal verify examples/minimal.mal.gal
gal verify examples/minimal.mal.gal --json
gal verify-all examples --json
gal parse examples/dialects/hal.gal --json
gal format examples/dialects/hal.gal
gal convert examples/dialects/hal.gal --to dot
gal convert examples/dialects/hal.gal --to yaml
gal convert examples/dialects/hal.gal --to cypher
gal convert ast.json --from json --to gal
gal load examples/dialects/hal.gal --mode plan
gal load examples/dialects/hal.gal --mode replay
gal components --json
gal dialects
gal dialects --json
gal schemas
gal schemas gal.verify_report.v0
gal schemas --write-dir docs/schemas
```

The current CLI shape is:

```bash
gal --version
gal doctor
gal examples
gal examples --name minimal.mal.gal
gal examples --write-dir ./gal-examples
gal init graph.gal
gal init graph.gal --dialect hal.v0 --force
gal init graph.gal --json
gal parse graph.gal --json
gal format graph.gal
gal verify graph.gal
gal verify graph.gal --json
gal verify-all graph.gal examples/
gal convert graph.gal --to json
gal convert graph.gal --to dot
gal convert graph.gal --to yaml
gal convert graph.gal --to cypher
gal convert ast.json --from json --to gal
gal load graph.gal --mode verify
gal load graph.gal --mode plan
gal load graph.gal --mode replay
gal load graph.gal --mode merge --runtime-json runtime.json
gal components
gal components --kind net-op --json
gal dialects
gal dialects --json
gal schemas
gal schemas gal.verify_batch.v0
gal schemas --write-dir docs/schemas
```

`gal verify` parses, canonicalizes, checks semantic round-trip, and validates the
declared `@dialect` against vocabulary blocks loaded from `docs/dialects/*.md`.
It checks node kinds, fields, relations, net operations, net input signals,
standing operations, and threads. It also checks registered component metadata
for reusable net and standing operations, including core net operation arity.
Use `--no-dialect` to run only syntax and round-trip verification, or
`--dialect-dir <path>` to point at another dialect spec directory.
Use `--json` to emit a structured verification report for CI or adapters.
`gal verify-all` accepts files and directories, recursively checks `*.gal`
files, and returns a batch report.

`gal init` creates a starter GAL file for a registered dialect. It defaults to
`mal.v0`, refuses to overwrite existing files unless `--force` is supplied, and
can create missing parent directories with `--parents`. Use `--json` to emit a
structured `gal.init_report.v0` report for scripts and adapters.

`gal examples` lists bundled example files that ship inside the package. Use
`--json` to emit a structured `gal.examples.v0` registry, `--name <example>` to
print one example, or `--write-dir <path>` to copy examples into a workspace.

`gal load` is currently an in-memory loader contract. It reports intended
changes for `plan`, checks runtime agreement for `verify`, builds a fresh
runtime state for `replay`, and applies changes into an existing runtime JSON for
`merge`.

`gal components` builds a small component registry from the loaded dialect
vocabularies. The registry currently covers reusable `netOps` and
`standingOps`, including source dialects, supported threads, and known net
operation arity.

GitHub Actions runs the same core checks on push and pull request: unit tests,
package build verification, `gal verify-all examples --json`, and CLI smoke
commands.
CI also installs the built wheel in a temporary environment and checks that the
bundled dialect registry works outside a source checkout.
The test suite also validates emitted CLI payloads against the JSON Schemas
published by `gal schemas`.

`gal schemas` lists the machine-readable JSON Schema contracts for the current
CLI payloads. Pass a schema id, such as `gal.verify_report.v0`, to emit that
schema as JSON.
Use `gal schemas --write-dir docs/schemas` to regenerate the static schema files
published by GitHub Pages.
