# 0.1% Pre-release TODO

Status snapshot for the current hardening sprint.

## Product polish

- [x] Add a visual README gallery with real app screenshots.
- [x] Ensure README links and API paths exactly match current implementation.
- [x] Add a concise release checklist for future updates.

## Release operations

- [x] Add automated changelog + version/tag + GitHub release workflow.
- [x] Bootstrap `CHANGELOG.md` for the current baseline release.

## Security and governance

- [x] Add security workflows (CodeQL + dependency review).
- [x] Add dependency update automation (Dependabot).
- [x] Add `SECURITY.md` and clear vulnerability disclosure instructions.
- [x] Add CODEOWNERS and PR/Issue templates.

## Developer experience and quality

- [x] Add ergonomic setup targets (`make install`, `make install-hooks`).
- [x] Add local pre-commit guardrails for lint/type/test.
- [x] Keep contributor docs aligned with real commands and repository URLs.

## Validation

- [x] Run full quality gate (`make check && make test && make e2e`) after all changes.
