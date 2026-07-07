# OAL: Observability Abstraction Layer

Status: draft v0.1.

OAL is the GAL dialect for observability graphs. It describes metrics, logs,
traces, monitors, alerts, service-level objectives, incidents, dashboards, and
diagnostic evidence.

## Vocabulary

```json
{
  "id": "oal.v0",
  "nodeKinds": ["signal", "metric", "log", "trace", "monitor", "alert", "slo", "incident", "dashboard", "probe"],
  "relations": ["observes", "samples", "aggregates", "alerts_on", "correlates_with", "suppresses", "escalates_to", "owned_by", "explains", "contradicts"],
  "fields": ["value", "threshold", "severity", "confidence", "freshness", "noise", "impact"],
  "signals": ["healthy", "degraded", "breaching", "noisy", "stale", "page", "suppress", "correlated"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["sample", "aggregate", "alert", "suppress", "correlate", "escalate", "annotate"],
  "threads": ["tick", "observe", "incident"]
}
```

## Node Kinds

| kind | purpose |
|---|---|
| `signal` | normalized runtime signal |
| `metric` | numeric measurement stream |
| `log` | log-derived evidence |
| `trace` | request or span trace |
| `monitor` | evaluation configuration |
| `alert` | notification condition |
| `slo` | service-level objective |
| `incident` | active or historical incident |
| `dashboard` | visualization surface |
| `probe` | synthetic or active check |

## Required Loader Rules

- `alert` nodes must identify monitored signals or explain missing selectors.
- `suppress` operations must include a bounded reason or expiry.
- `incident` nodes should preserve impact and escalation edges.
- `verify` mode must detect stale monitors and missing ownership.

## Example

```gal
@gal netlist.v0
@dialect oal.v0

metric_api_5xx "API 5xx rate" value(0.018) threshold(0.020) freshness(0.96) [kind: metric] [window: 5m]
monitor_api_errors "API error monitor" confidence(0.88) noise(0.12) [kind: monitor]
observes> metric_api_5xx(1.0)
alerts_on> alert_api_errors(0.9)

alert_api_errors "API error budget alert" severity(0.70) [kind: alert] [route: platform-oncall]
slo_api_availability "API availability SLO" threshold(0.999) [kind: slo]
metric_api_5xx correlates_with> trace_checkout_failures(0.72)

net should_page and2 breaching page
net hold_alert or2 suppress noisy
addf sample0 observe [metric: metric_api_5xx] [window: 5m]
addf correlate0 tick [service: svc_api] [window: 15m]
setp alert_api_errors.severity 0.80
```
