# AUDAL: Audit Abstraction Layer

Status: draft v0.1.

AUDAL is the GAL dialect for audit graphs: evidence, attestations, receipts,
controls, trails, immutable references, and compliance checks.

## Vocabulary

```json
{
  "id": "audal.v0",
  "nodeKinds": ["evidence", "attestation", "receipt", "control", "trail", "actor", "action", "finding", "scope"],
  "relations": ["attests", "evidences", "performed_by", "covers", "finds", "remediated_by", "derived_from", "signed_by"],
  "fields": ["confidence", "integrity", "currency", "coverage", "severity", "status", "risk"],
  "signals": ["complete", "missing", "signed", "tampered", "expired", "remediated", "audit_ready"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["collect", "attest", "verify_integrity", "detect_gap", "export_trail", "expire_evidence"],
  "threads": ["tick", "audit", "export"]
}
```

## Loader Rules

- `receipt` nodes should include immutable references when available.
- `signed_by` edges must not imply signature verification without evidence.
- Audit export must preserve ordering and provenance.

## Example

```gal
@gal netlist.v0
@dialect audal.v0

receipt_pages_deploy "GitHub Pages deploy receipt" integrity(0.96) currency(0.98) [kind: receipt]
attestation_public_docs "Public docs deployed attestation" confidence(0.92) [kind: attestation]
evidences> receipt_pages_deploy(1.0)
control_pages_workflow "Pages workflow control" coverage(0.80) [kind: control]
covers> attestation_public_docs(0.8)

net audit_ready and2 complete signed
addf verify_integrity0 audit [receipt: receipt_pages_deploy]
setp attestation_public_docs.confidence 0.94
```
