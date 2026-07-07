# GOVAL: Governance Abstraction Layer

Status: draft v0.1.

GOVAL is the GAL dialect for governance graphs: ownership, authority, review
gates, lifecycle status, stewardship, and escalation.

## Vocabulary

```json
{
  "id": "goval.v0",
  "nodeKinds": ["owner", "authority", "steward", "review", "gate", "charter", "lifecycle", "escalation", "exception"],
  "relations": ["owns", "approves", "reviews", "escalates_to", "delegates_to", "governs", "charters", "retires", "exempts"],
  "fields": ["authority", "confidence", "priority", "currency", "coverage", "risk", "status"],
  "signals": ["approved", "pending", "expired", "escalated", "owned", "ungoverned", "reviewed"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["review", "escalate", "expire_exception", "check_ownership", "attest", "retire"],
  "threads": ["tick", "governance", "review"]
}
```

## Loader Rules

- `exception` nodes must include owner, reason, and expiry.
- `owns` edges should be auditable and current.
- `escalate` operations must preserve trigger reason and destination.

## Example

```gal
@gal netlist.v0
@dialect goval.v0

owner_platform "Platform owner" authority(0.92) currency(0.95) [kind: owner]
charter_gal "GAL project charter" coverage(0.70) [kind: charter]
review_dialect_set "Dialect set review" status(0.40) priority(0.75) [kind: review]
owner_platform owns> charter_gal(1.0)
reviews> review_dialect_set(0.9)

net governance_ok and2 owned reviewed
addf check_ownership0 governance [target: charter_gal] [cadence: monthly]
setp review_dialect_set.status 0.65
```
