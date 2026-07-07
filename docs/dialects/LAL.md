# LAL: Learning Abstraction Layer

Status: draft v0.1.

LAL is the GAL dialect for learning graphs: examples, feedback, evaluations,
preference updates, model behavior changes, and calibration.

## Vocabulary

```json
{
  "id": "lal.v0",
  "nodeKinds": ["example", "feedback", "evaluation", "preference", "lesson", "model", "dataset", "metric", "update"],
  "relations": ["trains", "evaluates", "improves", "regresses", "supports", "contradicts", "derived_from", "applies_to"],
  "fields": ["score", "confidence", "drift", "coverage", "loss", "gain", "risk"],
  "signals": ["learned", "regressed", "improved", "stable", "needs_data", "calibrated", "validated"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["evaluate", "calibrate", "detect_drift", "ingest_feedback", "promote_lesson", "compare_model"],
  "threads": ["tick", "learn", "eval"]
}
```

## Loader Rules

- `feedback` nodes should retain source and target context.
- `preference` updates must distinguish observed preference from inferred
  preference.
- Evaluation nodes should preserve dataset and metric references.

## Example

```gal
@gal netlist.v0
@dialect lal.v0

eval_parser_roundtrip "Parser round-trip evaluation" score(0.91) coverage(0.86) [kind: evaluation]
metric_semantic_equiv "Semantic equivalence metric" confidence(0.88) [kind: metric]
evaluates> metric_semantic_equiv(1.0)
lesson_ast_first "Keep AST as converter boundary" confidence(0.90) [kind: lesson]
derived_from> eval_parser_roundtrip(0.8)

net promote_lesson and2 validated stable
addf calibrate0 eval [metric: metric_semantic_equiv] [window: 30d]
setp eval_parser_roundtrip.coverage 0.90
```
