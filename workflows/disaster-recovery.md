---
name: disaster-recovery
description: DR plan creation, failover testing, backup restoration, RPO/RTO validation, and DR drills.
type: pipeline
triggers:
  - dr-plan
  - failover-test
  - backup-restoration
  - rpo-rto-validation
variants:
  small:
    description: Single component DR test or backup restoration drill.
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Comprehensive DR plan creation and multi-system failover testing.
    gates: [design, final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: regulated
    add: [compliance]
    add-roles: [atlas-compliance]
  - if: data-changes
    add-roles: [atlas-data-eng, atlas-dba]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: disaster recovery

Hope for the best. Plan for the worst. Test your plans.

## Variant selection

Pick variant based on scope:
- **small:** single component backup restoration test, simple failover drill
- **full:** multi-system DR plan, full failover testing, compliance requirements

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### dr-assessment
- **Gate:** design (full only)
- **Parallel:** false
- **Roles:** atlas-devops (standard), atlas-dba (standard for data stores), atlas-architect (standard for system-wide)
- **Input:** system architecture, current backup config, business requirements
- **Output:** dr-assessment.md (RPO/RTO targets, current capabilities vs targets, gaps identified)

### dr-implementation
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard), atlas-dba (standard)
- **Input:** dr-assessment.md, gaps to close
- **Output:** implementation summary (backup procedures, failover scripts, runbooks created/updated)

### failover-testing
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard), atlas-qa (standard for verification)
- **Input:** dr implementation, test plan
- **Output:** test-results.md (failover executed, data integrity verified, RPO/RTO met)

### drill-execution
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-devops (standard), atlas-dba (standard)
- **Input:** validated DR implementation
- **Output:** drill-report.md (full drill executed, timeline documented, lessons learned, gaps closed)

## Definition of Done per gate

### Design gate (full only)
- [ ] RPO and RTO targets documented and agreed with business
- [ ] Current capabilities compared against targets
- [ ] Gaps identified with a remediation plan
- [ ] User has signed off on the DR design

### Final gate (auto-approve if small)
- [ ] Backup procedures tested (restoration verified, not just backup completion)
- [ ] Failover tested end-to-end (not just the switch, but data integrity post-failover)
- [ ] Runbooks created for each DR scenario
- [ ] DR drill executed and results documented
- [ ] Lessons learned captured and action items assigned
- [ ] User has signed off (full only; small auto-approves)
