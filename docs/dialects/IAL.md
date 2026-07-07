# IAL: Interface Abstraction Layer

Status: draft v0.1.

IAL is the GAL dialect for interface graphs: APIs, contracts, schemas, protocol
boundaries, compatibility, and version negotiation.

## Vocabulary

```json
{
  "id": "ial.v0",
  "nodeKinds": ["interface", "endpoint", "method", "schema", "contract", "client", "server", "protocol", "version"],
  "relations": ["implements", "calls", "accepts", "returns", "version_of", "compatible_with", "breaks", "owned_by", "depends_on"],
  "fields": ["version", "stability", "compatibility", "latency", "error_rate", "coverage", "risk"],
  "signals": ["compatible", "breaking", "deprecated", "stable", "covered", "available"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["lint_contract", "diff_schema", "check_compat", "publish_contract", "deprecate"],
  "threads": ["tick", "contract", "release"]
}
```

## Loader Rules

- `breaks` edges must include affected version or contract context.
- `compatible_with` edges should be symmetric only when the dialect validator
  confirms bidirectional compatibility.
- Contract checks must be read-only in `verify` mode.

## Example

```gal
@gal netlist.v0
@dialect ial.v0

api_orders "Orders API" stability(0.88) compatibility(0.93) [kind: interface]
schema_order_v3 "Order schema v3" version(3) coverage(0.91) [kind: schema]
endpoint_create_order "Create order endpoint" latency(0.14) [kind: endpoint]
implements> schema_order_v3(1.0)
api_orders calls> endpoint_create_order(1.0)

net release_safe and2 compatible covered
addf check_compat0 contract [interface: api_orders] [target: schema_order_v3]
setp api_orders.compatibility 0.95
```
