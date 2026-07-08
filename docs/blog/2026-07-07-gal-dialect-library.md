---
title: "The GAL Dialect Library"
status: draft
date: 2026-07-07
image: ../assets/blog/gal-dialect-library.png
---

# The GAL Dialect Library

![Abstract graph runtime library showing specialized dialect shelves](../assets/blog/gal-dialect-library.png)

GAL starts with a deliberately small contract: a graph can be expressed as
nodes, edges, signal nets, standing operations, and parameter updates. The
dialect library keeps that syntax stable while letting different runtime
domains define their own validation vocabulary.

The core idea is that a deployment graph, a memory graph, and a hardware graph
should not need three unrelated file formats. They need different node kinds,
relations, fields, signals, and standing operations over the same inspectable
graph shape.

## What the Library Contains

The current draft set includes 22 dialects:

- Foundation: MAL, HAL, KAL, ReAL, CAL, IAL.
- Runtime: DAL, RAL, SAL, EAL, TAL, WAL, OAL.
- Assurance: PAL, QAL, FAL, GOVAL, RISKAL, AUDAL, VAL, LAL.
- Agent operations: AAL for agents, tools, tasks, plans, and handoffs.

Each dialect is optional. A release graph can load DAL, PAL, OAL, RISKAL, and
VAL without carrying learning or knowledge semantics. An agentic runtime can
load AAL, CAL, ReAL, MAL, and AUDAL without modeling physical topology.

## Why Markdown Specs

Each dialect lives as a readable Markdown document with one JSON vocabulary
block. The CLI loads the JSON block as the registry and leaves the surrounding
text for human design intent, loader rules, and examples.

That keeps the repo simple: the same source file is useful to a maintainer, a
validator, a package user, and the static documentation site.

## How to Try It

```bash
gal dialects
gal examples
gal verify examples/dialects/hal.gal
gal components --json
```

The long-term goal is not to make every runtime use every dialect. The goal is
to make cross-domain graph state explicit enough that adapters can inspect,
verify, and exchange it without losing meaning.
