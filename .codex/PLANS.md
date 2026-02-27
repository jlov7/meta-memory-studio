# Pre-release Excellence Plan

## Purpose / Big Picture

Ship MetaMemory Studio in a state that feels close to production quality for an open-source pre-release:
- deterministic quality gates,
- release and changelog automation,
- security/governance hygiene,
- polished docs and visuals,
- repeatable local workflow guardrails.

## Progress

- [x] Establish execution plan and tracking files.
- [x] Add release automation and changelog flow.
- [x] Add security workflows and repository governance templates.
- [x] Upgrade developer workflow guardrails (`make`, hooks, docs consistency).
- [x] Add screenshot capture pipeline and README visual gallery.
- [ ] Commit and push.

## Surprises & Discoveries

- Existing docs are strong but contain stale endpoint/clone URL references.
- Root-level Next/Turbopack lockfile warning is external to repo and currently non-blocking.

## Decision Log

- Prioritize reliability and repeatability over novelty; every enhancement must be automatable and testable.
- Keep existing architecture intact; only add additive quality systems.

## Risks & Validation Gates

- Risk: CI additions may introduce flaky or slow jobs.
  - Gate: run `make check && make test && make e2e` locally after all changes.
- Risk: README/doc updates drift from implementation.
  - Gate: cross-check API paths against backend router declarations.

## Outcomes & Retrospective

- Completed: release automation, security/governance workflows, contributor templates, local hooks, docs alignment, visual gallery automation, and full quality verification.
- Not completed: none in scope for this sweep.
- Lesson: automated screenshot generation should run with same-origin URLs to avoid local CORS preflight errors during docs capture.
