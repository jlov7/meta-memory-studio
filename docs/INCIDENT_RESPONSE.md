# Incident Response

## Severity levels

- SEV0: Active data loss/corruption or confirmed critical exposure; widespread impact
- SEV1: Major feature unavailable or strong evidence of high-risk security issue
- SEV2: Partial degradation or moderate security risk with workaround
- SEV3: Minor issue with limited scope and no immediate risk

## Response targets

- SEV0: acknowledge within 15 minutes, contain within 60 minutes
- SEV1: acknowledge within 30 minutes, contain within 4 hours
- SEV2: acknowledge within 4 business hours, mitigate within 2 business days
- SEV3: triage in normal backlog cycle

## Workflow

1. Detect
- Trigger from tests, CI, monitoring, or user report.

2. Triage
- Assign severity, impact scope, and incident owner.
- Capture current commit SHA and environment.

3. Contain
- Disable risky workflows/feature flags where possible.
- Rate-limit or temporarily block abusive write paths.
- For data-quality incidents, pause new ingest jobs.

4. Eradicate and recover
- Apply fix on a hotfix branch.
- Run `make check && make test` and targeted `make e2e`.
- Restore data if required using DB backup/restore scripts.

5. Communicate
- Provide status updates at a fixed interval (SEV0/SEV1: every 30 minutes).
- Log timeline of actions and outcomes.

6. Close and learn
- Publish post-incident notes: root cause, impact, timeline, corrective actions.
- Add regression tests and update runbook/checklists.

## Evidence to preserve

- Failing command outputs
- Relevant request IDs from API responses/logs
- Database backup snapshot used for recovery
- Commit(s) containing mitigation and permanent fix
