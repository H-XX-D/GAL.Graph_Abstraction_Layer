# ReAL: Reasoning Abstraction Layer

Status: draft v0.1.

ReAL is the GAL dialect for reasoning graphs: hypotheses, plans, critiques,
arguments, uncertainty, decisions, and decision traces. The dialect id is
`real.v0` to avoid colliding with `ral.v0` for resources.

## Vocabulary

```json
{
  "id": "real.v0",
  "nodeKinds": ["hypothesis", "argument", "premise", "inference", "critique", "decision", "option", "plan", "assumption"],
  "relations": ["supports", "contradicts", "depends_on", "infers", "critiques", "chooses", "rejects", "assumes", "revises"],
  "fields": ["confidence", "uncertainty", "utility", "cost", "risk", "priority", "coherence"],
  "signals": ["plausible", "refuted", "chosen", "blocked", "needs_evidence", "coherent", "revised"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["evaluate", "compare", "critique", "revise", "choose", "trace"],
  "threads": ["tick", "reason", "review"]
}
```

## Loader Rules

- `decision` nodes should preserve rejected options when available.
- `assumption` nodes should be marked when unverified.
- `trace` operations must report the chain of premises and inferences.

## Example

```gal
@gal netlist.v0
@dialect real.v0

hyp_parser_first "Build parser before loaders" confidence(0.78) utility(0.82) [kind: hypothesis]
option_parser "Parser-first roadmap option" cost(0.30) risk(0.24) [kind: option]
supports> hyp_parser_first(0.9)
decision_next "Choose parser and renderer next" confidence(0.84) [kind: decision]
chooses> option_parser(1.0)

net decision_ready and2 plausible coherent
addf compare0 reason [options: option_parser option_loader] [criterion: utility]
setp hyp_parser_first.confidence 0.82
```
