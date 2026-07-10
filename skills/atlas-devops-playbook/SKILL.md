---
name: atlas-devops-playbook
description: DevOps playbook for atlas-devops.
type: playbook
appliesTo: [atlas-devops]
tags: [playbook, devops, cicd, sre]
---

# atlas-devops

## Route
- CI/CD pipeline setup → devops
- infrastructure as code → devops
- deployment, release → devops
- monitoring, alerting → devops
- SRE practices → devops
- rollback procedures → devops

## Knowledge
- Google SRE (SLO/SLI, error budgets) → k/google-sre-practices
- DORA metrics → k/dora-metrics
- GitOps principles → k/gitops-principles
- AWS Well-Architected → k/aws-well-architected
- Anti-patterns → k/anti-patterns

## Scope
CI/CD pipelines, infrastructure as code, deployment, release management, monitoring, alerting, SRE practices, rollback procedures | NOT application code (→ dev), security controls (→ security), test strategy (→ qa), architecture decisions (→ architect)

## Delegation Examples
### Pipeline setup
"Set up CI/CD for new service." → devops: build/test/scan/deploy pipeline, IaC for staging, rollback steps, health checks, observability.

### Production incident
"Service degraded after deploy." → devops: check recent deployments, prepare rollback, verify monitoring, coordinate with maintenance for root cause.

### Release preparation
"Cut release candidate." → devops: verify pipeline passes all gates, staged rollout plan, canary monitoring, auto-rollback if SLO breach.
