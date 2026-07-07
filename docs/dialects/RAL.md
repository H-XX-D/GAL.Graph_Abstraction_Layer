# RAL: Resource Abstraction Layer

Status: draft v0.1.

RAL is the GAL dialect for resource graphs: compute, storage, network,
capacity, quota, allocation, and placement.

## Vocabulary

```json
{
  "id": "ral.v0",
  "nodeKinds": ["resource", "pool", "quota", "allocation", "compute", "storage", "network", "region", "tenant"],
  "relations": ["allocates", "reserved_for", "consumes", "hosts", "located_in", "constrained_by", "scales_with", "depends_on"],
  "fields": ["capacity", "used", "available", "cost", "latency", "pressure", "risk"],
  "signals": ["available", "saturated", "over_quota", "underused", "movable", "reserved"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["measure", "allocate", "rebalance", "forecast", "enforce_quota", "place"],
  "threads": ["tick", "scheduler", "capacity"]
}
```

## Loader Rules

- `quota` nodes should identify a tenant, scope, and limit.
- `allocation` nodes should reference a resource and consumer.
- `rebalance` and `place` operations must report planned movement in `plan`
  mode before applying changes.

## Example

```gal
@gal netlist.v0
@dialect ral.v0

pool_compute_us "US compute pool" capacity(1000) used(640) pressure(0.64) [kind: pool]
quota_platform "Platform quota" capacity(400) used(310) [kind: quota] [tenant: platform]
allocation_api "API compute allocation" used(120) [kind: allocation]
reserved_for> svc_api(1.0)
consumes> pool_compute_us(0.12)

net resource_ok and2 available not_over_quota
addf forecast0 capacity [pool: pool_compute_us] [window: 7d]
setp quota_platform.capacity 450
```
