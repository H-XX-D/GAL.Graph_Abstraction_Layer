# EAL: Event Abstraction Layer

Status: draft v0.1.

EAL is the GAL dialect for event graphs: events, streams, triggers, causality,
subscriptions, replay, and delivery state.

## Vocabulary

```json
{
  "id": "eal.v0",
  "nodeKinds": ["event", "stream", "topic", "subscription", "trigger", "handler", "replay", "cursor", "dead_letter"],
  "relations": ["publishes_to", "subscribes_to", "triggers", "handled_by", "caused_by", "replays", "routes_to", "dead_letters_to"],
  "fields": ["offset", "lag", "rate", "freshness", "retries", "ordering", "risk"],
  "signals": ["received", "ordered", "late", "dropped", "replayable", "poisoned", "caught_up"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["consume", "publish", "replay", "dedupe", "route", "dead_letter"],
  "threads": ["tick", "event", "replay"]
}
```

## Loader Rules

- `replay` operations must define a bounded cursor or time range.
- `dead_letter` nodes should preserve original topic and failure reason.
- Causal edges must remain directed and auditable.

## Example

```gal
@gal netlist.v0
@dialect eal.v0

topic_orders "Orders topic" rate(240) lag(0.03) [kind: topic]
sub_billing "Billing subscription" lag(12) retries(1) [kind: subscription]
subscribes_to> topic_orders(1.0)
handler_billing "Billing event handler" freshness(0.94) [kind: handler]
handled_by> handler_billing(1.0)

net consumer_ok and2 received caught_up
addf consume0 event [subscription: sub_billing] [batch: 100]
setp consume0.batch 250
```
