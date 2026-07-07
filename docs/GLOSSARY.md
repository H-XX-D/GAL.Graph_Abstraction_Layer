# Glossary

## GAL

Graph Abstraction Layer. A small interchange layer for graph-runtime state and
graph-oriented operations.

## GAL:netlist

The first concrete GAL syntax profile. It is a line-oriented format for graph facts,
signal wiring, standing operations, and runtime parameter changes.

## MAL

Memory Abstraction Language. MAL is the memory-focused dialect of GAL, expressed
through the GAL:netlist syntax.

## Dialect

A vocabulary and validation layer on top of GAL syntax. A dialect defines legal
node kinds, relation names, fields, signals, operations, threads, and loader
behavior.

## Node

An entity in the graph, written as an identifier, label, compact fields, and
optional bracket parameters.

## Edge

A directed typed relation between graph entities.

## Net

Signal wiring through a reusable operation.

## Standing Operation

A reusable graph operation scheduled on a runtime thread, such as `tick`.

## Parameter Set

A runtime tuning line that updates a parameter on an existing node, net, or
standing operation.

## Canonical AST

The stable interop surface used by parsers, renderers, converters, and loaders.

## Semantic Round-Trip

The requirement that parsing text, rendering canonical text, and parsing again
produces an equivalent AST.
