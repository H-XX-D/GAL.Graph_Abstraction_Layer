# FAL: Failure Abstraction Layer

Status: draft v0.1.

FAL is the GAL dialect for failure graphs: failure modes, blast radius, recovery
paths, mitigations, fault injection, and resilience evidence.

## Vocabulary

```json
{
  "id": "fal.v0",
  "nodeKinds": ["failure", "mode", "fault", "blast_radius", "mitigation", "recovery", "experiment", "fallback", "runbook"],
  "relations": ["causes", "impacts", "mitigated_by", "recovers_via", "falls_back_to", "detected_by", "depends_on", "validated_by"],
  "fields": ["severity", "likelihood", "impact", "detectability", "coverage", "recovery_time", "risk"],
  "signals": ["failed", "degraded", "contained", "recoverable", "mitigated", "validated", "unknown"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["inject_fault", "simulate", "estimate_blast_radius", "verify_recovery", "update_runbook"],
  "threads": ["tick", "failure", "experiment"]
}
```

## Loader Rules

- `inject_fault` operations must be explicit about safety mode and target.
- `blast_radius` nodes should identify impacted services or topology.
- Recovery paths must preserve validation evidence when available.

## Example

```gal
@gal netlist.v0
@dialect fal.v0

failure_db_lag "Database replica lag failure" severity(0.72) likelihood(0.22) [kind: failure]
blast_checkout "Checkout blast radius" impact(0.48) [kind: blast_radius]
mitigation_read_primary "Read from primary mitigation" coverage(0.75) [kind: mitigation]
impacts> blast_checkout(0.8)
mitigated_by> mitigation_read_primary(0.7)

net resilient and2 mitigated recoverable
addf verify_recovery0 failure [failure: failure_db_lag] [mode: tabletop]
setp failure_db_lag.likelihood 0.18
```
