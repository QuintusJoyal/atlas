---
name: refactoring
description: Systematic code improvement. Analyze, plan, refactor, test, review.
type: pipeline
triggers:
  - refactor
  - cleanup
  - modernize
  - tech-debt
variants:
  small:
    description: Simple refactoring, no design phase.
    gates: [final]
    skip: [design]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Complex refactoring with design review.
    gates: [design, final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: refactoring

Systematic code improvement. Analyze current state, plan changes, refactor, test, review.

## Variant selection

- **small:** local refactoring, <10 files, no API changes
- **full:** cross-module refactoring, API changes, or architecture improvements

## Phases

### analyze
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (standard)
- **Input:** target files, codebase context
- **Output:** analysis summary (current state, issues found, improvement opportunities)

### design
- **Gate:** design
- **Parallel:** false
- **Roles:** atlas-architect (premium)
- **Input:** analysis summary
- **Output:** refactoring plan (target state, migration steps, risk assessment)
- **Skip-if:** variant=small

### refactor
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (fast)
- **Input:** refactoring plan (full) or analysis summary (small)
- **Output:** implementation summary (files changed, approach, test results)

### test
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-qa (standard)
- **Input:** implementation summary, original analysis
- **Output:** test results (regression tests pass, new tests added)

### review
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-reviewer (premium)
- **Input:** implementation diff, test results
- **Output:** review.md (verdict, findings)

## Definition of Done

- [ ] All existing tests pass
- [ ] Code coverage maintained or improved
- [ ] No new warnings or errors
- [ ] Documentation updated if API changed
- [ ] User has signed off
