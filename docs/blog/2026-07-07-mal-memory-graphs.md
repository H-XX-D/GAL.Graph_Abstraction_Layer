---
title: "MAL and Durable Memory Graphs"
status: draft
date: 2026-07-07
image: ../assets/blog/mal-memory-graphs.png
---

# MAL and Durable Memory Graphs

![Memory graph with claims, observations, evidence, contradiction, and standing programs](../assets/blog/mal-memory-graphs.png)

MAL is the Memory Abstraction Language dialect for GAL:netlist. It models memory
as graph state rather than as a flat pile of notes.

The first-class objects are claims, observations, tasks, and memory programs.
Edges say whether one object supports, contradicts, concerns, or depends on
another. Fields carry confidence, effective confidence, currency, salience,
uncertainty, and concern. Signals expose states such as weak, stale, review,
pinned, annexed, and high concern.

## Why Contradiction Is Explicit

Durable memory needs a way to correct itself without silently overwriting
history. MAL uses explicit `contradicts` edges so old claims can be demoted
while the audit path remains visible.

That gives loaders and retrieval systems enough structure to answer a practical
question: which memory should be trusted now, and what evidence changed the
answer?

## Standing Programs

MAL also includes standing operations such as `watch`, `drift`, `trend`,
`quorum`, and `emit_witness`. These are not parser side effects. They are
inspectable runtime intents that a loader can plan, verify, replay, or merge.

```gal
claim_ab12 "API is degraded" conf(0.82) eff(0.76) curr(0.91) [kind: claim]
concerns> service_api(0.9)
supports> log_cd34(0.8)

net alert or2 high_concern stale
addf watch0 tick [topics: api-status] [measure: effective_confidence]
```

The wider GAL library uses MAL as a shape reference: compact vocabulary,
explicit loader rules, and examples that round-trip through the same canonical
AST as every other dialect.
