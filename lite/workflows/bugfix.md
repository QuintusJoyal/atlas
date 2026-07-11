# Bugfix (Lite)

## Phase 1: Investigate
- **Roles:** atlas-maintenance or atlas-dev
- **Input:** bug report, error logs
- **Output:** root cause, affected files, reproduction steps
- **Gate:** auto (root cause identified)

## Phase 2: Fix + Test
- **Roles:** atlas-dev (fix) → atlas-qa (test)
- **Input:** root cause analysis
- **Output:** code fix, regression test
- **Gate:** tests pass, regression covered

## Phase 3: Review
- **Roles:** atlas-reviewer
- **Input:** code diff, test results
- **Output:** review verdict
- **Gate:** user approves

## Definition of Done
- [ ] Root cause identified with evidence
- [ ] Regression test added and passing
- [ ] Code reviewed
- [ ] User approves
