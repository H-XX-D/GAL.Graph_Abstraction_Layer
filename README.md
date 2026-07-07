# GAL.Graph_Abstraction_Layer

Graph Abstraction Layer defines a small, inspectable interchange layer for graph
runtime state.

The first concrete syntax profile is `GAL:netlist`: a line-oriented format for
nodes, edges, signal wiring, standing operations, and runtime parameter changes.
MAL is a memory-focused dialect of GAL, expressed through the GAL:netlist syntax.

## Current Status

Status: draft v0.1.

This repository is in the definition phase. The immediate goal is to freeze the
core AST shape, validate the line grammar with examples, and then build a small
parser/renderer pair with semantic round-trip tests.

## Repository Map

- [GAL_NETLIST_SPEC.md](GAL_NETLIST_SPEC.md): draft GAL:netlist specification.
- [docs/ROADMAP.md](docs/ROADMAP.md): implementation and refinement milestones.
- [docs/GLOSSARY.md](docs/GLOSSARY.md): working terms and vocabulary.
- [docs/dialects/](docs/dialects/): draft GAL dialect specifications.
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

## First Implementation Milestones

1. Freeze the AST categories and error shape.
2. Implement parser support for headers, nodes, bodies, edges, nets, schedules,
   parameter sets, and comments.
3. Implement canonical rendering.
4. Add semantic round-trip tests and fixture examples.
5. Add JSON, DOT, and YAML conversion commands.

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
the dialects it needs, and cross-dialect edges should stay explicit.

## Development Notes

Install the local CLI in editable mode:

```bash
python3 -m pip install -e ".[dev]"
```

Run the current checks:

```bash
python3 -m pytest -q
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
```

The current CLI shape is:

```bash
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

`gal load` is currently an in-memory loader contract. It reports intended
changes for `plan`, checks runtime agreement for `verify`, builds a fresh
runtime state for `replay`, and applies changes into an existing runtime JSON for
`merge`.

`gal components` builds a small component registry from the loaded dialect
vocabularies. The registry currently covers reusable `netOps` and
`standingOps`, including source dialects, supported threads, and known net
operation arity.

GitHub Actions runs the same core checks on push and pull request: unit tests,
`gal verify-all examples --json`, and CLI smoke commands.

`gal schemas` lists the machine-readable JSON Schema contracts for the current
CLI payloads. Pass a schema id, such as `gal.verify_report.v0`, to emit that
schema as JSON.
