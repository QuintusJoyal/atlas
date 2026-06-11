---
name: atlas-devops-playbook
description: DevOps methodology for atlas-devops: CI/CD, IaC, release and rollback, and DORA. Use when atlas-devops runs.
disable-model-invocation: true
---

# DevOps and SRE playbook

Standards: DORA metrics, SRE and SLO practices, infrastructure as code, secure CI/CD, 12-factor delivery.

## CI/CD
Build, test, scan, and deploy as code. Fail fast. Keep pipelines fast and deterministic. No secrets in pipeline config.

## Infrastructure as code
Declarative, version-controlled, reviewable. Same change path as application code.

## Release and rollback checklist
- [ ] Change is behind a flag or is reversible
- [ ] Rollback steps written and tested
- [ ] Health checks and alerts in place
- [ ] Observability: logs, metrics, traces
- [ ] Post-deploy verification defined

## DORA signals
Deployment frequency, lead time for changes, change failure rate, time to restore.

## Deployment artifact
Pipeline or release steps, IaC changes, rollback plan, observability checks. Persist to `.atlas/runs/<run-id>/deploy.md`. Pipeline changes via MCP need user approval.

## References
- https://dora.dev/
- https://sre.google/sre-book/table-of-contents/
