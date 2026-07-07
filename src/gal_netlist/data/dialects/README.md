# GAL Dialect Specifications

This directory defines first-pass GAL dialects. Each dialect uses the same
GAL:netlist syntax and specializes vocabulary, validation, and loader behavior
for a runtime domain.

The current draft dialect set:

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

The set is intentionally broad, but dialects are optional lenses rather than a
mandatory stack. A deployment graph might use DAL, PAL, OAL, and VAL without
loading learning or knowledge semantics. An agentic runtime might use AAL, CAL,
ReAL, MAL, and AUDAL without carrying topology vocabulary.

See [TAXONOMY.md](TAXONOMY.md) for grouping and selection guidance.

## Shared Dialect Contract

A GAL dialect defines:

- Node kinds accepted by `[kind: ...]`.
- Relation names accepted by edge lines.
- Compact fields accepted on nodes.
- Signal names used by `net` lines.
- Standing operation bases accepted by `addf`.
- Threads accepted by scheduled operations.
- Loader rules for verification, planning, merge, and replay.

Dialects do not define new syntax. They constrain and interpret GAL:netlist.

## Cross-Dialect Edge Pattern

Cross-domain graphs should keep relation names explicit and domain-owned:

```gal
release_api "API release 2026.07.06" status(0.70) [kind: release]
governed_by> policy_change_window(1.0)
observed_by> monitor_api_errors(1.0)
executed_by> agent_deploy0(0.9)
```

The target node may belong to another dialect, but the edge still parses as a
normal GAL edge. Dialect validators can warn or reject cross-dialect relations
depending on runtime policy.
