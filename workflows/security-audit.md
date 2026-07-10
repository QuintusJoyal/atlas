---
name: security-audit
description: Read-only assessment. No code changes.
type: assessment
triggers:
  - security-review
  - compliance-audit
  - vulnerability-assessment
variants:
  small:
    description: Targeted audit of specific component or flow. Single gate.
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Comprehensive audit across multiple components. Full gates.
    gates: [scope, final]
    token-estimate: medium-heavy
    kickoff: standard
    auto-approve: false
    tracking: full
conditions: []
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: security-audit

Read-only assessment. No code changes.

## Variant selection

Pick variant based on scope:
- **small:** single component, specific flow, targeted assessment
- **full:** full system audit, multi-component, compliance assessment

Tell the user which variant you picked and why.

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### scope
- **Gate:** scope (full only)
- **Parallel:** false
- **Roles:** atlas-pm (standard) or atlas-consultant (standard)
- **Skip-if:** variant=small
- **Input:** user request, targets
- **Output:** scope.md (targets, threat model boundaries, assessment criteria)

### audit
- **Gate:** null
- **Parallel:** true
- **Roles:** atlas-security (premium), atlas-compliance (premium if regulated)
- **Input:** scope.md, codebase access
- **Output:** findings (OWASP, STRIDE, secrets, vulnerabilities, compliance gaps)

### review
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-reviewer (premium)
- **Input:** audit findings
- **Output:** review.md (quality and charter conformance)

### report
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-docs (fast)
- **Input:** audit findings, review
- **Output:** audit report (findings by severity, compliance gaps, remediation)

## Definition of Done (auto-approve if small)

- [ ] Findings by severity with concrete remediation
- [ ] Compliance gaps mapped to frameworks
- [ ] Clear, prioritized report for the user
- [ ] No changes applied (read-only)
- [ ] User has signed off (full only; small auto-approves if all above pass)
