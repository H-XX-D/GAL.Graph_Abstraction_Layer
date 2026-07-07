# RISKAL: Risk Abstraction Layer

Status: draft v0.1.

RISKAL is the GAL dialect for risk graphs: risks, controls, mitigations,
exposure, residual risk, acceptance, and review cadence.

## Vocabulary

```json
{
  "id": "riskal.v0",
  "nodeKinds": ["risk", "control", "mitigation", "exposure", "asset", "threat", "acceptance", "review", "scenario"],
  "relations": ["threatens", "exposes", "mitigated_by", "controlled_by", "accepted_by", "reviewed_by", "depends_on", "increases", "reduces"],
  "fields": ["likelihood", "impact", "severity", "residual", "confidence", "coverage", "priority"],
  "signals": ["accepted", "unaccepted", "mitigated", "exposed", "high_risk", "review_due", "controlled"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["score_risk", "review", "expire_acceptance", "test_control", "rank_mitigation"],
  "threads": ["tick", "risk", "review"]
}
```

## Loader Rules

- `acceptance` nodes must include owner, scope, and expiry.
- `residual` values must be recalculated or marked stale after control changes.
- `high_risk` signals should be routed to governance or policy dialects.

## Example

```gal
@gal netlist.v0
@dialect riskal.v0

risk_unreviewed_deploy "Unreviewed production deploy risk" likelihood(0.22) impact(0.72) residual(0.40) [kind: risk]
control_release_review "Release review control" coverage(0.84) [kind: control]
mitigated_by> control_release_review(0.8)
asset_prod "Production environment" priority(0.95) [kind: asset]
threatens> asset_prod(0.7)

net risk_ok and2 mitigated controlled
addf score_risk0 risk [risk: risk_unreviewed_deploy] [method: likelihood_impact]
setp risk_unreviewed_deploy.residual 0.32
```
