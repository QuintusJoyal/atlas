---
name: gitops-principles
load-when: Setting up deployment pipelines, managing infrastructure as code, reconciliation
skip-when: Incident management (see itil-incident-management), metrics (see dora-metrics)
---

# GitOps Principles

## Quick Reference
- Git as single source of truth for infrastructure and application config
- Desired state declared in Git, actual state reconciled automatically
- Changes via pull requests, not manual commands
- Drift detection: system alerts when actual state differs from desired state
- Declarative, versioned, automated, agent-based

## Deep Dive

### Four GitOps Principles
1. **Declarative**: describe desired state, not how to get there
2. **Versioned**: all config stored in Git with full history
3. **Automated**: agents reconcile desired state automatically
4. **Software agents**: controllers that observe, diff, and act

### How GitOps Works
1. Developer pushes config change to Git
2. CI pipeline validates (lint, test, security scan)
3. GitOps agent detects change
4. Agent compares desired state (Git) with actual state (cluster)
5. Agent applies changes to reconcile

### Drift Detection
- Agent continuously checks actual vs desired state
- If drift detected, agent either auto-reconciles or alerts
- Manual changes are reverted to Git state
- This ensures auditability and consistency

### GitOps Tools
- **ArgoCD**: GitOps operator for Kubernetes
- **Flux**: GitOps toolkit for Kubernetes
- **Crossplane**: infrastructure as code via Kubernetes
- **Terraform Cloud**: state management and drift detection

### Best Practices
- One repo per environment or one repo with overlays
- Separate app code from config (different repos or directories)
- Use branch protection for production configs
- Implement automated validation before merge
- Use sealed secrets or external secret management

### GitOps vs CI/CD
CI/CD = how to build and deploy. GitOps = how to manage what's deployed.
They complement each other: CI builds, CD deploys, GitOps manages state.

## See Also
- **google-sre-practices** — SRE practices for reliable operations
- **dora-metrics** — Measuring deployment performance
- **aws-well-architected** — Cloud architecture best practices
- **finops-practices** — Cost optimization for infrastructure
