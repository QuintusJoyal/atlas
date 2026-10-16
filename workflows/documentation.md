---
name: documentation
description: Documentation-only changes. Draft, review, publish.
type: pipeline
triggers:
  - documentation
  - readme
  - changelog
  - runbook
  - docs
variants:
  small:
    description: Simple doc update, no review gate.
    gates: []
    skip: [review]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Complex documentation with review gate.
    gates: [final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions: []
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: documentation

Documentation-only changes. Draft content, review for accuracy, publish.

## Variant selection

- **small:** typo fixes, minor updates, README tweaks
- **full:** new documentation, runbooks, API docs, changelogs

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### draft
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-docs (standard)
- **Input:** documentation requirements, source material
- **Output:** draft documentation

### review
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-reviewer (premium)
- **Input:** draft documentation, source code (if applicable)
- **Output:** review.md (accuracy, completeness, clarity)
- **Skip-if:** variant=small

### publish
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-docs (standard)
- **Input:** reviewed documentation
- **Output:** published documentation (final files)

## Definition of Done

- [ ] Documentation accurate (matches code/behavior)
- [ ] Documentation complete (covers all required topics)
- [ ] Documentation clear (no jargon, good examples)
- [ ] User has signed off (full variant only; small has no gate)
