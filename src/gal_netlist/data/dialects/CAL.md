# CAL: Capability Abstraction Layer

Status: draft v0.1.

CAL is the GAL dialect for capability graphs: permissions, affordances, grants,
tool access, delegated authority, and capability negotiation.

## Vocabulary

```json
{
  "id": "cal.v0",
  "nodeKinds": ["capability", "grant", "principal", "tool", "permission", "scope", "delegation", "revocation", "request"],
  "relations": ["grants", "permits", "requires", "delegates_to", "scoped_to", "revokes", "requested_by", "owned_by"],
  "fields": ["confidence", "risk", "priority", "currency", "trust", "blast_radius"],
  "signals": ["granted", "revoked", "expired", "insufficient", "negotiable", "privileged", "scoped"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["authorize", "negotiate", "revoke", "attest", "detect_excess", "request_grant"],
  "threads": ["tick", "authz", "review"]
}
```

## Loader Rules

- `grant` nodes must identify principal, capability, and scope.
- Privileged grants must preserve approval or policy evidence.
- `revoke` operations must be represented as explicit graph changes.

## Example

```gal
@gal netlist.v0
@dialect cal.v0

principal_deploy_agent "Deploy agent" trust(0.82) [kind: principal]
cap_repo_write "Repository write capability" risk(0.44) [kind: capability]
grant_deploy_repo "Deploy agent repo write grant" currency(0.91) [kind: grant]
grants> cap_repo_write(1.0)
scoped_to> scope_gal_repo(1.0)

net can_write and2 granted scoped
addf authorize0 authz [principal: principal_deploy_agent] [capability: cap_repo_write]
setp grant_deploy_repo.risk 0.30
```
