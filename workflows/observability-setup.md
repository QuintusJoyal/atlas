---
name: observability-setup
description: Define SLOs, instrument code, create dashboards, set alerts, validate monitoring.
type: standard
triggers:
  - new-service
  - observability-gap
  - alerting-gap
  - slo-definition
variants:
  small:
    description: Basic observability for a single service (metrics, logging, one dashboard).
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Comprehensive observability (SLOs, metrics, logs, traces, dashboards, alerts, runbooks).
    gates: [design, final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: security-sensitive
    add: [security-review]
    add-roles: [atlas-security]
  - if: regulated
    add: [compliance]
    add-roles: [atlas-compliance]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: observability setup

If you can't see it, you can't fix it. Observability is not optional.

## Variant selection

Pick variant based on scope:
- **small:** single service, basic metrics (golden signals), one dashboard, simple alert
- **full:** multi-service, SLOs defined, metrics + logs + traces, dashboards, alert routing, runbooks

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, write budget.md
- **Lightweight:** create run folder, start immediately

## Phases

### slo-definition
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard), atlas-architect (standard for system-wide SLOs)
- **Input:** service description, user-facing requirements, SLA commitments
- **Output:** slo-spec.md (SLIs defined, SLO targets, error budgets, measurement approach)

### instrumentation
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (standard)
- **Input:** slo-spec.md, application code
- **Output:** implementation summary (metrics instrumented, log format, trace propagation)

### dashboards-and-alerts
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard)
- **Input:** slo-spec.md, instrumentation output
- **Output:** observability-artifact.md (dashboard URLs, alert rules, notification channels)

### validation
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-qa (standard), atlas-devops (standard)
- **Input:** all observability artifacts
- **Output:** validation report (dashboards render correctly, alerts fire on test data, SLO measurement works)

## Definition of Done

- [ ] SLIs defined and measurable (latency, error rate, throughput)
- [ ] SLO targets set with error budgets calculated
- [ ] Dashboards show golden signals for the service
- [ ] Alerts fire on real issues (tested with synthetic data)
- [ ] Alert routing reaches the right people/channels
- [ ] Runbooks exist for each alert
- [ ] User has signed off (full only; small auto-approves)
