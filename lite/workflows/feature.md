# Feature (Lite)

## Phase 1: Requirements
- **Roles:** atlas-pm (or atlas-ba)
- **Input:** user request
- **Output:** requirements.md (user stories, acceptance criteria)
- **Gate:** user approves

## Phase 2: Design
- **Roles:** atlas-architect (+ atlas-ux if UI involved)
- **Input:** requirements.md
- **Output:** design.md (architecture, components, trade-offs)
- **Gate:** user approves

## Phase 3: Implementation + Testing
- **Roles:** atlas-dev (implement) → atlas-qa (test)
- **Input:** design.md, requirements.md
- **Output:** code changes, test results
- **Gate:** tests pass

## Phase 4: Review + Deploy
- **Roles:** atlas-reviewer → atlas-devops
- **Input:** code diff, test results
- **Output:** review verdict, deployment
- **Gate:** user approves

## Definition of Done
- [ ] Requirements approved by user
- [ ] Design approved by user
- [ ] All tests passing
- [ ] Code reviewed
- [ ] User approves final delivery
