---
name: delivery-governance
description: Delivery governance: release gates, rollback procedures, change management, deployment standards. Load when delivery or release tasks are in motion.
load: on-demand
---

# Delivery governance

Deliveries that cannot be rolled back should not be delivered.

## Release gates
- Every release passes through defined gates: build, test, security scan, approval, deploy.
- Gates are mandatory. No gate skipping without documented waiver from the user.
- Reference: `k/quality-gates.md` for gate definitions.

## Rollback readiness
- Before any deployment: (1) verify rollback procedure exists, (2) test rollback on staging, (3) confirm rollback artifact is available.
- Document rollback steps in the deployment runbook.
- Feature flags enable rollback without redeployment where possible.

## Change management
- Classify changes: standard (pre-approved), normal (review required), emergency (post-review).
- Standard changes: documented procedures executed by authorized roles.
- Emergency changes: deploy first, document and review within 24 hours.

## Deployment practices
- Blue-green or canary deployments for production. No big-bang deployments.
- Feature flags for progressive rollout. Start small, monitor, expand.
- Reference: `k/gitops-principles.md` for GitOps-based deployments.

## Versioning
- Semantic versioning: MAJOR.MINOR.PATCH. Breaking changes increment MAJOR.
- Changelog maintained for every release. Human-readable, user-facing.
- Reference: `k/conventional-commits.md`.

## Post-deployment
- Monitor for 15-30 minutes after deployment. Watch error rates, latency, and key metrics.
- If anomalies detected, roll back immediately. Investigate after stability is restored.
- Document deployment outcomes: what was deployed, any issues, resolution.
