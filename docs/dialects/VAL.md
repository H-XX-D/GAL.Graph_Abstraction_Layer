# VAL: Verification Abstraction Layer

Status: draft v0.1.

VAL is the GAL dialect for verification graphs: tests, checks, proofs,
validation results, acceptance criteria, and release gates.

## Vocabulary

```json
{
  "id": "val.v0",
  "nodeKinds": ["test", "check", "proof", "criterion", "result", "suite", "oracle", "fixture", "gate"],
  "relations": ["verifies", "fails", "passes", "covers", "depends_on", "proves", "invalidates", "gates", "uses_fixture"],
  "fields": ["status", "coverage", "confidence", "freshness", "duration", "flake_rate", "risk"],
  "signals": ["passed", "failed", "flaky", "covered", "verified", "blocked", "accepted"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["run_check", "run_suite", "prove", "compare_oracle", "detect_flake", "gate_release"],
  "threads": ["tick", "verify", "ci"]
}
```

## Loader Rules

- `result` nodes must preserve test identity, timestamp, and status.
- `proof` nodes should distinguish mechanized proof from informal argument.
- Release gates should reference required criteria and current results.

## Example

```gal
@gal netlist.v0
@dialect val.v0

suite_roundtrip "GAL round-trip suite" coverage(0.82) status(0.90) [kind: suite]
test_parse_render "Parse/render semantic equivalence test" confidence(0.88) [kind: test]
covers> criterion_semantic_equiv(1.0)
result_roundtrip_pass "Round-trip suite passed" status(1.0) freshness(0.96) [kind: result]
passes> test_parse_render(1.0)

net gate_ok and2 passed covered
addf run_suite0 ci [suite: suite_roundtrip] [trigger: push]
setp suite_roundtrip.coverage 0.90
```
