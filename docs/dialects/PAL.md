# PAL: Policy Abstraction Layer

Status: draft v0.1.

PAL is the GAL dialect for policy graphs. It describes rules, scopes,
obligations, constraints, approvals, exceptions, and decisions.

## Vocabulary

```json
{
  "id": "pal.v0",
  "nodeKinds": ["policy", "rule", "scope", "subject", "resource", "action", "obligation", "exception", "decision", "approval"],
  "relations": ["applies_to", "permits", "denies", "requires", "exempts", "delegates_to", "overrides", "evaluates", "governs", "supports", "contradicts"],
  "fields": ["confidence", "priority", "severity", "currency", "risk", "compliance"],
  "signals": ["allowed", "denied", "needs_review", "exception_active", "expired", "conflict", "compliant"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["evaluate", "audit", "expire", "detect_conflict", "request_approval", "attest"],
  "threads": ["tick", "decision", "audit"]
}
```

## Node Kinds

| kind | purpose |
|---|---|
| `policy` | named policy container |
| `rule` | atomic policy rule |
| `scope` | condition set for applicability |
| `subject` | actor or principal |
| `resource` | protected target |
| `action` | requested operation |
| `obligation` | required follow-up action |
| `exception` | bounded policy bypass |
| `decision` | allow, deny, or review result |
| `approval` | approval artifact or record |

## Required Loader Rules

- `exception` nodes must include an owner and expiry parameter.
- `decision` nodes should retain the evaluated subject, action, and resource.
- `overrides` and `contradicts` relations must preserve priority information
  when present.
- Loaders must support read-only `verify` and `audit` behavior.

## Example

```gal
@gal netlist.v0
@dialect pal.v0

policy_deploy_windows "Production deploy windows" priority(0.80) compliance(0.92) [kind: policy]
rule_weekday_window "Deploy only during approved weekday windows" severity(0.70) [kind: rule]
applies_to> scope_prod_deploy(1.0)
requires> approval_release_manager(0.9)

scope_prod_deploy "Production deployment scope" [kind: scope] [environment: prod] [action: deploy]
approval_release_manager "Release manager approval" currency(0.88) [kind: approval] [owner: release-management]

net policy_ok and2 allowed compliant
net review_needed or2 needs_review conflict
addf evaluate0 decision [subject: agent_deploy0] [resource: env_prod] [action: deploy]
addf expire0 tick [kind: exception] [within: 24h]
setp evaluate0.mode strict
```
