# MAL: Memory Abstraction Language

Status: draft v0.1.

MAL is the GAL dialect for memory graphs: claims, observations, evidence,
confidence, currency, salience, contradiction, and standing memory programs.

## Vocabulary

```json
{
  "id": "mal.v0",
  "nodeKinds": ["claim", "obs", "task", "prg"],
  "relations": ["supports", "contradicts", "concerns", "depends_on"],
  "fields": ["conf", "eff", "curr", "sal", "unc", "concern"],
  "signals": ["weak", "stale", "review", "pinned", "annexed", "high_concern"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["score", "emit_witness", "tag_projection", "watch", "drift", "quorum", "trend", "reflex", "allocate"],
  "threads": ["tick"]
}
```

## Loader Rules

- `claim` and `obs` nodes should preserve confidence and provenance when
  available.
- `contradicts` edges should be explicit so stale memory can be demoted rather
  than silently overwritten.
- Standing operations must be read-only during parse and validation.
- Runtime loaders should report confidence, currency, salience, and concern
  changes rather than hiding them behind opaque state updates.

## Example

```gal
@gal netlist.v0
@dialect mal.v0

claim_ab12 "API is degraded" conf(0.82) eff(0.76) curr(0.91) sal(0.44) [kind: claim] [topics: api-status]
body "Five-minute error window exceeded normal baseline."
concerns> service_api(0.9)
supports> log_cd34(0.8)

net alert or2 high_concern stale
net route lut5 weak stale review pinned annexed

addf watch0 tick [topics: api-status] [measure: effective_confidence] [delta: 0.20]
addf drift0 tick [topics: api-status] [measure: currency] [delta: 0.30]
setp watch0.delta 0.25
```
