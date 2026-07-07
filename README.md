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
| `mal.v0` | Memory Abstraction Language | claims, evidence, memory programs |
| `dal.v0` | Deployment Abstraction Layer | services, releases, rollout state |
| `pal.v0` | Policy Abstraction Layer | rules, obligations, decisions |
| `aal.v0` | Agent Abstraction Layer | agents, tools, tasks, handoffs |
| `wal.v0` | Workflow Abstraction Layer | steps, jobs, gates, retries |
| `oal.v0` | Observability Abstraction Layer | signals, alerts, traces, monitors |
| `hal.v0` | Hardware Abstraction Layer | devices, buses, drivers, firmware, capabilities |
| `ral.v0` | Resource Abstraction Layer | compute, storage, network, quota |
| `sal.v0` | State Abstraction Layer | state, snapshots, migrations, consistency |
| `eal.v0` | Event Abstraction Layer | events, streams, triggers, replay |
| `cal.v0` | Capability Abstraction Layer | permissions, tools, grants, negotiation |
| `ial.v0` | Interface Abstraction Layer | APIs, contracts, schemas, protocols |
| `tal.v0` | Topology Abstraction Layer | regions, clusters, routes, placement |
| `qal.v0` | Quality Abstraction Layer | SLOs, guarantees, constraints, correctness |
| `fal.v0` | Failure Abstraction Layer | failures, blast radius, recovery paths |
| `kal.v0` | Knowledge Abstraction Layer | concepts, sources, provenance |
| `real.v0` | Reasoning Abstraction Layer | hypotheses, plans, critiques, decisions |
| `lal.v0` | Learning Abstraction Layer | examples, feedback, evaluations, preference updates |
| `goval.v0` | Governance Abstraction Layer | ownership, authority, lifecycle, escalation |
| `riskal.v0` | Risk Abstraction Layer | risks, controls, mitigations, acceptance |
| `audal.v0` | Audit Abstraction Layer | evidence, attestations, receipts, trails |
| `val.v0` | Verification Abstraction Layer | tests, checks, proofs, acceptance criteria |

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
gal parse examples/dialects/hal.gal --json
gal format examples/dialects/hal.gal
```

The current CLI shape is:

```bash
gal parse graph.gal --json
gal format graph.gal
gal verify graph.gal
gal convert graph.gal --to json
```
