---
name: infra-change
description: Infrastructure, network, or cloud changes with IaC, testing, and staged rollout.
type: standard
triggers:
  - infrastructure-change
  - cloud-migration
  - network-change
  - ia
  - deployment
variants:
  small:
    description: Simple infrastructure change, backward-compatible, low risk.
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Complex infrastructure change with multi-system impact, compliance, or cost implications.
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
  - if: data-changes
    add: [data-validation]
    add-roles: [atlas-data-eng]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: infra-change (Lite)

Infrastructure changes are high-risk. Design for reversibility. Test in staging. Rollback first, analyze later.

## Variant selection

- **small:** single resource change, backward-compatible, IaC update
- **full:** multi-system change, network topology, compliance review needed

## Phases

### planning
- **Roles:** atlas-devops, atlas-architect
- **Input:** change requirements, current infrastructure
- **Output:** change plan (IaC diff, impact assessment, rollback plan)

### implementation
- **Roles:** atlas-devops
- **Input:** change plan
- **Output:** implementation summary (IaC applied, configuration changes)

### validation
- **Roles:** atlas-qa, atlas-devops
- **Input:** implementation summary
- **Output:** validation report (functionality verified, monitoring confirmed)

### delivery
- **Gate:** final
- **Roles:** atlas-devops
- **Input:** validated change
- **Output:** deployment artifact (staged rollout complete)

## Definition of Done

- [ ] Change applied in staging first
- [ ] Rollback plan tested
- [ ] Monitoring confirms no regression
- [ ] Cost impact assessed (if applicable)
- [ ] User has signed off
