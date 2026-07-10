---
name: infra-change
description: Infrastructure, network, or cloud changes. Mandatory security gate.
type: pipeline
triggers:
  - infrastructure
  - cloud
  - network-change
variants:
  small:
    description: Small infra change, single gate. Skip requirements/design gates.
    gates: [final]
    skip: [requirements-gate, design-gate, design]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Full infra pipeline with all gates. Mandatory security gate.
    gates: [requirements, design, final]
    token-estimate: medium-heavy
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

# Workflow: infra-change

Infrastructure, network, or cloud changes. Mandatory security gate.

## Variant selection

Pick variant based on scope and blast radius:
- **small:** config change, single resource, no network changes, no new services
- **full:** new service, network changes, cloud migration, multi-resource, regulated

Tell the user which variant you picked and why.

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### requirements
- **Gate:** requirements
- **Parallel:** false
- **Roles:** atlas-pm (standard) or atlas-delivery (standard)
- **Skip-if:** variant=small
- **Input:** user goal or infrastructure request
- **Output:** requirements.md (target state, constraints, blast radius)

### design
- **Gate:** design
- **Parallel:** true
- **Roles:** atlas-cloud (premium), atlas-sysinfra (standard), atlas-network (standard), atlas-ent-arch (premium)
- **Skip-if:** variant=small
- **Input:** requirements.md
- **Output:** design.md (architecture, security controls, cost, rollback plan)

### implement
- **Gate:** null
- **Parallel:** true
- **Roles:** atlas-devops (standard), atlas-sysinfra (standard), atlas-network (standard)
- **Input:** design.md, IaC templates
- **Output:** implementation summary (IaC changes, config changes, test results)

### security-review
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-security (premium, mandatory)
- **Input:** design.md, implementation diff
- **Output:** security-assessment.md (findings, gate verdict)

### review
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-reviewer (premium)
- **Input:** implementation diff, security findings
- **Output:** review.md (verdict, findings)

### apply
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard)
- **Input:** merge approval, security clearance
- **Output:** deployment artifact (apply, verify, rollback ready)

## Definition of Done per gate

### Requirements gate (full only)
- [ ] Target state and constraints clear
- [ ] Blast radius understood
- [ ] User has signed off

### Design gate (full only)
- [ ] Architecture approved
- [ ] Security controls documented
- [ ] Cost noted
- [ ] Rollback planned
- [ ] User has signed off

### Final delivery gate (auto-approve if small)
- [ ] Security cleared
- [ ] Change reversible
- [ ] Observability and alerts in place
- [ ] Documentation complete
- [ ] User has signed off (full only; small auto-approves if all above pass)
