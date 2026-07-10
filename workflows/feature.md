---
name: feature
description: Full pipeline for net-new work. All three approval gates plus token-budget kickoff.
type: pipeline
triggers:
  - net-new-work
  - feature-request
  - enhancement
variants:
  small:
    description: Small feature, single gate. Skip design phase and requirements/design gates.
    gates: [final]
    skip: [requirements-gate, design-gate, design]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Full pipeline with all gates. Standard kickoff with estimation huddle.
    gates: [requirements, design, final]
    token-estimate: medium-heavy
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: regulated
    add: [compliance]
    add-roles: [atlas-compliance]
  - if: data-changes
    add-roles: [atlas-data-eng, atlas-dba]
  - if: security-sensitive
    add: [security-review]
    add-roles: [atlas-security]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: feature

Full pipeline for net-new work. All three approval gates plus token-budget kickoff.

## Variant selection

Pick variant based on scope and complexity:
- **small:** scope is clear, <3 files changed, no new services, no security/compliance concerns
- **full:** new service, new API, auth changes, data model changes, regulated domain, or unclear scope

Tell the user which variant you picked and why.

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### requirements
- **Gate:** requirements
- **Parallel:** false
- **Roles:** atlas-pm (standard), atlas-ba (fast)
- **Skip-if:** variant=small
- **Input:** user goal or feature request
- **Output:** requirements.md (user stories, acceptance criteria, MoSCoW, scope)

### design
- **Gate:** design
- **Parallel:** true
- **Roles:** atlas-architect (premium), atlas-ux (standard)
- **Skip-if:** variant=small
- **Input:** requirements.md
- **Output:** design.md (C4 diagrams, ADRs, NFRs, trade-offs)

### implementation
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (fast)
- **Input:** design.md (full) or requirements.md (small), API contracts
- **Output:** implementation summary (files changed, approach, test results)

### testing
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-qa (standard)
- **Input:** implementation summary, acceptance criteria
- **Output:** test-plan.md (test results, coverage, bug reports)

### review
- **Gate:** final
- **Parallel:** true
- **Roles:** atlas-reviewer (premium), atlas-security (premium)
- **Input:** implementation diff, test results, security findings
- **Output:** review.md (verdict, findings by severity)

### deploy
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard)
- **Input:** merge approval, security clearance
- **Output:** deployment artifact (pipeline, IaC, rollback plan)

## Definition of Done per gate

### Requirements gate (full only)
- [ ] All user stories have testable acceptance criteria
- [ ] Non-functional requirements specified (performance, security, availability)
- [ ] Edge cases documented
- [ ] Scope and out-of-scope explicit
- [ ] User has signed off

### Design gate (full only)
- [ ] Architecture approved (ADR recorded)
- [ ] Security review complete (atlas-security sign-off)
- [ ] API contracts defined (request/response schemas)
- [ ] NFRs measurable (specific targets, not vague aspirations)
- [ ] Trade-offs noted

### Final delivery gate (auto-approve if small)
- [ ] All tests pass (unit, integration, E2E as applicable)
- [ ] Security scan clean (no critical/high findings)
- [ ] Documentation complete (README, changelog, runbook as applicable)
- [ ] Rollback plan exists and has been tested
- [ ] User has signed off (full only; small auto-approves if all above pass)
