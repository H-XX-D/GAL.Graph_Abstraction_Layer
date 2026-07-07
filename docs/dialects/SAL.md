# SAL: State Abstraction Layer

Status: draft v0.1.

SAL is the GAL dialect for state graphs: durable state, ephemeral state,
snapshots, migrations, consistency models, and recovery points.

## Vocabulary

```json
{
  "id": "sal.v0",
  "nodeKinds": ["state", "store", "snapshot", "migration", "schema", "replica", "lock", "transaction", "checkpoint"],
  "relations": ["stored_in", "replicates_to", "derived_from", "migrates_to", "guards", "commits", "rolls_back_to", "depends_on"],
  "fields": ["version", "freshness", "lag", "consistency", "durability", "size", "risk"],
  "signals": ["consistent", "dirty", "locked", "migrating", "snapshotted", "recoverable", "lagging"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["snapshot", "migrate", "replicate", "compact", "verify_state", "recover"],
  "threads": ["tick", "state", "migration"]
}
```

## Loader Rules

- `migration` nodes must identify source and target schema versions.
- `snapshot` operations must preserve a recovery reference.
- `verify_state` must not mutate state in `verify` mode.

## Example

```gal
@gal netlist.v0
@dialect sal.v0

store_orders "Orders store" consistency(0.92) durability(0.99) lag(0.02) [kind: store]
schema_orders_v3 "Orders schema v3" version(3) [kind: schema]
migration_orders_v4 "Orders schema migration v4" risk(0.28) [kind: migration]
migrates_to> schema_orders_v3(1.0)
stored_in> store_orders(1.0)

net migration_ready and2 consistent snapshotted
addf snapshot0 state [store: store_orders] [retention: 14d]
setp migration_orders_v4.risk 0.22
```
