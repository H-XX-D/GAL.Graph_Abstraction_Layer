# QAL: Quality Abstraction Layer

Status: draft v0.1.

QAL is the GAL dialect for quality graphs: SLOs, guarantees, constraints,
correctness, durability, availability, and acceptance quality.

## Vocabulary

```json
{
  "id": "qal.v0",
  "nodeKinds": ["quality", "slo", "guarantee", "constraint", "criterion", "measurement", "defect", "waiver", "target"],
  "relations": ["measures", "satisfies", "violates", "constrains", "waives", "depends_on", "owned_by", "supports"],
  "fields": ["score", "target", "actual", "severity", "confidence", "freshness", "risk"],
  "signals": ["passing", "failing", "waived", "regressed", "improving", "measured", "at_risk"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["measure", "score", "detect_regression", "verify_quality", "expire_waiver"],
  "threads": ["tick", "quality", "review"]
}
```

## Loader Rules

- `waiver` nodes must include owner, reason, and expiry.
- `constraint` violations should preserve measured and target values.
- `score` operations must declare their inputs.

## Example

```gal
@gal netlist.v0
@dialect qal.v0

slo_api_latency "API latency SLO" target(0.95) actual(0.92) risk(0.34) [kind: slo]
measurement_p95 "API p95 latency measurement" score(0.92) freshness(0.97) [kind: measurement]
measures> slo_api_latency(1.0)
violates> criterion_latency(0.7)

net quality_ok and2 passing measured
addf detect_regression0 quality [target: slo_api_latency] [window: 7d]
setp slo_api_latency.actual 0.94
```
