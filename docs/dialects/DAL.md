# DAL: Deployment Abstraction Layer

Status: draft v0.1.

DAL is the GAL dialect for deployment graphs. It describes services, artifacts,
environments, releases, rollout strategy, health gates, and rollback paths.

## Vocabulary

```json
{
  "id": "dal.v0",
  "nodeKinds": ["service", "artifact", "environment", "release", "rollout", "gate", "secret_ref", "endpoint"],
  "relations": ["deploys_to", "depends_on", "contains", "promotes_to", "rolls_back_to", "guarded_by", "exposes", "uses_secret", "observed_by", "governed_by", "executed_by"],
  "fields": ["status", "risk", "progress", "health", "latency", "error_rate"],
  "signals": ["healthy", "degraded", "blocked", "canary_passed", "rollback_ready", "policy_ok", "traffic_shifted"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["health_check", "rollout", "rollback", "promote", "diff_env", "verify_artifact"],
  "threads": ["tick", "deploy", "rollback"]
}
```

## Node Kinds

| kind | purpose |
|---|---|
| `service` | deployable runtime service |
| `artifact` | immutable deployable build output |
| `environment` | target runtime environment |
| `release` | deployment attempt or release record |
| `rollout` | traffic or instance rollout plan |
| `gate` | deploy-time condition |
| `secret_ref` | reference to an external secret, never the secret value |
| `endpoint` | public or internal network endpoint |

## Required Loader Rules

- `secret_ref` nodes must never include raw secret material in labels, bodies, or
  bracket parameters.
- `release` nodes should identify the target artifact and environment through
  `contains`, `deploys_to`, or `promotes_to` edges.
- `rollback` operations must reference a `rolls_back_to` edge or report a
  validation warning.
- `plan` mode must report intended changes without touching deployment systems.

## Example

```gal
@gal netlist.v0
@dialect dal.v0

svc_api "Public API service" health(0.94) error_rate(0.01) [kind: service] [owner: platform]
artifact_api_20260706 "api:2026.07.06" status(1.0) [kind: artifact] [sha: sha256:example]
env_prod "Production" health(0.96) [kind: environment] [region: us-east-1]
release_api_20260706 "API release 2026.07.06" progress(0.25) risk(0.31) [kind: release]
contains> artifact_api_20260706(1.0)
deploys_to> env_prod(1.0)
guarded_by> gate_error_budget(1.0)

gate_error_budget "Error budget gate" status(0.85) [kind: gate] [threshold: 0.02]
net deploy_ok and2 healthy policy_ok
addf health_check0 tick [service: svc_api] [window: 5m]
addf rollout0 deploy [release: release_api_20260706] [strategy: canary] [percent: 10]
setp rollout0.percent 25
```
