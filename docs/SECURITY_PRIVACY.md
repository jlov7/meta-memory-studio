# Security & privacy

## Threat model (MVP)
- Trace tampering
- PII leakage in exports
- Cross-tenant data access
- Prompt injection stored as “memory”

## Controls
- Raw traces stored append-only + hash chain.
- Derived memory has explicit states:
  - active / deprecated / deleted
- PII tagging:
  - regex for emails/phones
  - allow manual override in UI
- Export modes:
  - Private: includes payloads
  - Public: strips payloads, keeps commitments

## Deletion semantics
- Soft delete:
  - hidden from retrieval
  - kept for audit
- Hard delete (forget):
  - removes payload/content
  - keeps tombstone audit record
  - verifies export/redaction

