# Dependency and Vulnerability Policy

## Scope

This policy applies to all dependencies in:
- `backend` (Python, managed by `uv`)
- `frontend` (Node.js, managed by `pnpm`)

## Source of truth

- Backend lockfile: `backend/uv.lock`
- Frontend lockfile: `frontend/pnpm-lock.yaml`
- CI/security scans: `.github/workflows/security.yml`
- Local SBOM/dependency manifests: `make sbom`

## Triage SLA

- Critical: triage within 24 hours, patch or mitigating control within 72 hours
- High: triage within 2 business days, patch within 7 calendar days
- Medium: triage within 7 calendar days, patch within 30 days
- Low: triage within 30 days, patch in next routine dependency update

## Decision rules

- If a fix is available and low-risk, patch immediately.
- If no fix exists, document temporary mitigation and monitor upstream advisories.
- If patch risk is high, pin current version with rationale and create a follow-up ticket.
- Never downgrade to a known vulnerable version to resolve compatibility quickly.

## Verification requirements

After dependency changes:
1. Run `make check`
2. Run `make test`
3. Run `make e2e` for release-bound changes
4. Regenerate dependency manifest with `make sbom`

## Release gate

A release is blocked if unresolved critical vulnerabilities exist in runtime dependencies without an approved mitigation note in the release record.
