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
