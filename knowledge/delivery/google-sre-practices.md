---
name: google-sre-practices
load-when: Defining SLOs, managing incidents, conducting postmortems, reducing toil
skip-when: Deployment pipelines (see dora-metrics), incident process (see itil-incident-management)
---

# Google SRE Practices

## Quick Reference
- SLO: target reliability level (e.g., 99.9%)
- SLI: metric that measures the SLO (e.g., request latency)
- Error budget: allowed failure (1 - SLO)
- Toil: manual, repetitive, automatable work
- Postmortem: blameless analysis of incidents

## Deep Dive

### SLO/SLI/Error Budget
- **SLI**: what you measure (availability, latency, throughput)
- **SLO**: what you promise (99.9% availability over 30 days)
- **Error budget**: what you can spend (0.1% = 43 minutes/month)

When error budget is spent, freeze feature releases and focus on reliability.

### Toil Reduction
Toil = manual, repetitive, scalable, tactical, no enduring value.
Target: reduce toil to <50% of engineering time.
Measure toil as a percentage of total work.

### Postmortem Process
1. Incident response and mitigation
2. Postmortem meeting (blameless)
3. Write postmortem document
4. Identify action items with owners and deadlines
5. Track action items to completion

### Postmortem Template
```markdown
## Incident Summary
- When: ...
- Duration: ...
- Impact: ...

## Timeline
- ...

## Root Cause
- ...

## What Went Well
- ...

## What Went Wrong
- ...

## Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| ... | ... | ... | ... |
```

### Key SRE Practices
- **Service Level Objectives**: define and track reliability targets
- **Error Budgets**: balance reliability vs feature velocity
- **Toil Reduction**: automate repetitive work
- **Capacity Planning**: ensure sufficient resources
- **Change Management**: safe, incremental deployments
- **Incident Management**: detect, respond, resolve, learn

## See Also
- **dora-metrics** — Delivery performance metrics
- **itil-incident-management** — Formal incident lifecycle
- **gitops-principles** — Deployment and reconciliation
- **anti-patterns** — Deployment and operational failures
