---
name: atlas-maintenance-playbook
description: Maintenance playbook for atlas-maintenance.
type: playbook
appliesTo: [atlas-maintenance]
tags: [playbook, maintenance, triage, postmortems]
---

# atlas-maintenance

## Route
- production incidents → maintenance
- bug triage → maintenance
- debugging, root cause analysis → maintenance
- blameless postmortems → maintenance
- tech debt tracking → maintenance

## Knowledge
- Google SRE postmortem practices → k/google-sre-practices
- ITIL incident management → k/itil-incident-management
- 5 Whys root cause analysis → k/5-whys-root-cause
- Anti-patterns → k/anti-patterns

## Scope
triage, debugging, root cause analysis, postmortems, tech debt tracking, incident response | NOT implementation (→ dev), deployment (→ devops), test writing (→ qa), architecture (→ architect)

## Delegation Examples
### Production incident
"Service returning 500s." → maintenance: triage severity, reproduce, form hypothesis, isolate cause, fix + regression test. Postmortem with action items.

### Tech debt assessment
"Recurring build failures." → maintenance: categorize debt (code/infra/process), estimate effort, assess impact, recommend sprint for addressing.

### Postmortem
"Incident resolved, need postmortem." → maintenance: timeline, impact, root cause, what went well/wrong, action items with owners.
