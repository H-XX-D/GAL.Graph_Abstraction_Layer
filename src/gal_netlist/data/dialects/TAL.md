# TAL: Topology Abstraction Layer

Status: draft v0.1.

TAL is the GAL dialect for topology graphs: nodes, regions, clusters, routes,
dependency layout, placement, and network adjacency.

## Vocabulary

```json
{
  "id": "tal.v0",
  "nodeKinds": ["node", "cluster", "region", "zone", "route", "link", "segment", "gateway", "placement"],
  "relations": ["contains", "connects_to", "routes_to", "placed_in", "adjacent_to", "depends_on", "isolates", "spans"],
  "fields": ["distance", "latency", "bandwidth", "health", "capacity", "risk", "redundancy"],
  "signals": ["reachable", "partitioned", "redundant", "isolated", "congested", "placed"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["route", "place", "probe_link", "rebalance", "detect_partition", "map_dependency"],
  "threads": ["tick", "topology", "route"]
}
```

## Loader Rules

- `connects_to` and `routes_to` must preserve direction.
- `placement` nodes should connect workload, resource, and topology target.
- Partition checks must report affected paths.

## Example

```gal
@gal netlist.v0
@dialect tal.v0

region_use1 "us-east-1" health(0.96) capacity(0.78) [kind: region]
cluster_api_a "API cluster A" redundancy(0.80) [kind: cluster]
route_api_edge "API edge route" latency(0.08) health(0.94) [kind: route]
placed_in> region_use1(1.0)
routes_to> cluster_api_a(1.0)

net path_ok and2 reachable redundant
addf probe_link0 topology [route: route_api_edge] [interval: 30s]
setp route_api_edge.latency 0.07
```
