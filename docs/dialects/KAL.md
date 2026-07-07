# KAL: Knowledge Abstraction Layer

Status: draft v0.1.

KAL is the GAL dialect for knowledge graphs: concepts, sources, claims,
definitions, provenance, derivations, and knowledge boundaries. MAL can reuse
KAL concepts while remaining the memory-specific GAL dialect.

## Vocabulary

```json
{
  "id": "kal.v0",
  "nodeKinds": ["concept", "claim", "source", "definition", "evidence", "derivation", "taxonomy", "boundary", "unknown"],
  "relations": ["defines", "supports", "contradicts", "derived_from", "cites", "part_of", "equivalent_to", "specializes", "uncertain_about"],
  "fields": ["confidence", "currency", "salience", "uncertainty", "coverage", "trust", "risk"],
  "signals": ["known", "uncertain", "contested", "stale", "supported", "derived", "canonical"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["classify", "derive", "reconcile", "refresh_source", "detect_contradiction", "summarize"],
  "threads": ["tick", "knowledge", "review"]
}
```

## Loader Rules

- `source` nodes should preserve provenance and retrieval context.
- `equivalent_to` should be validated before canonical render duplicates it.
- `unknown` nodes must carry a question or boundary.

## Example

```gal
@gal netlist.v0
@dialect kal.v0

concept_gal "Graph Abstraction Layer" confidence(0.92) currency(0.95) [kind: concept]
definition_gal "GAL defines graph-runtime interchange" confidence(0.88) [kind: definition]
defines> concept_gal(1.0)
source_spec "GAL netlist specification" trust(0.93) [kind: source]
cites> source_spec(1.0)

net knowledge_ok and2 supported canonical
addf reconcile0 knowledge [concept: concept_gal] [scope: dialects]
setp concept_gal.currency 0.98
```
