---
name: bugfix
description: Fast lane for defects. One final gate. Keep it cheap.
type: fast-lane
triggers:
  - bug-report
  - regression
  - user-issue
variants:
  small:
    description: Simple bugfix, no estimation huddle. Single final gate.
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Complex bugfix with estimation huddle. Security gate if risk is high.
    gates: [final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: security-impacting
    add: [security-review]
    add-roles: [atlas-security]
  - if: regulated
    add: [compliance]
    add-roles: [atlas-compliance]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: bugfix (and hotfix)

Fast lane for defects. One final gate. Keep it cheap.

## Variant selection

Pick variant based on scope and risk:
- **small:** clear root cause, <5 files changed, no auth/security/data changes
- **full:** unclear root cause, auth changes, data changes, or high-risk area

Tell the user which variant you picked and why.

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### triage
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-maintenance (fast) or atlas-dev (fast)
- **Input:** bug report, error logs, reproduction steps
- **Output:** triage summary (root cause, affected files, reproduction steps)

### fix
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (fast)
- **Input:** triage summary, affected code
- **Output:** implementation summary (files changed, fix approach, regression test)

### test
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-qa (standard)
- **Input:** implementation summary, original bug report
- **Output:** test results (regression test added, existing tests pass)

### review
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-reviewer (premium if risk is high, standard otherwise)
- **Input:** implementation diff, test results
- **Output:** review.md (verdict, findings)

### deploy
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard)
- **Input:** merge approval, security clearance (if applicable)
- **Output:** deployment artifact (hotfix: expedited, with rollback ready)

### retrospective
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-lead (standard)
- **Input:** trajectory.jsonl, quality scores, critic results, trust profiles
- **Output:** proposed changes (lessons, tool improvements, role corrections)
- **Human approval:** required for all knowledge updates
- **See:** `knowledge/knowledge-compounding.md`

## Definition of Done (auto-approve if small)

- [ ] Root cause identified with evidence (no guessing)
- [ ] Regression test added and passing
- [ ] Review clear; rollback ready for hotfix
- [ ] User has signed off (full only; small auto-approves if all above pass)
