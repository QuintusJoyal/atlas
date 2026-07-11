---
name: definition-of-done
load-when: Defining completion criteria, sprint planning, release readiness
skip-when: Quality gates (see quality-gates), review checklists (see review-checklists)
---

# Definition of Done (DoD)

## Quick Reference
- Shared understanding of what "done" means for every work item
- Applies to features, bugs, technical debt, and spikes
- Includes: code, tests, documentation, deployment, acceptance
- DoD is a contract between the team and stakeholders
- Violating DoD means it's not done

## Deep Dive

### DoD Checklist
```markdown
## Code
- [ ] Code reviewed and approved
- [ ] All tests passing
- [ ] No new warnings or errors
- [ ] Code follows style guide

## Testing
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] E2E tests for critical paths
- [ ] Edge cases covered

## Documentation
- [ ] API documentation updated
- [ ] User-facing docs updated (if applicable)
- [ ] Code comments for complex logic
- [ ] README updated (if applicable)

## Deployment
- [ ] Deployed to staging
- [ ] Smoke tests passing in staging
- [ ] Rollback plan documented
- [ ] Feature flag configured (if applicable)

## Acceptance
- [ ] Acceptance criteria met
- [ ] Product Owner verified
- [ ] Performance benchmarks met
- [ ] Security review completed (if applicable)
```

### When to Use
- Sprint planning: team commits to DoD for all items
- Code review: DoD is the checklist
- Release planning: all items must meet DoD
- Definition of Done is not negotiable per item

### DoD vs Acceptance Criteria
- **DoD**: applies to ALL work items (team standard)
- **Acceptance Criteria**: specific to ONE work item (feature-specific)

### Updating DoD
- Team reviews DoD in retrospectives
- Add items when gaps are discovered
- Remove items that don't add value
- DoD should evolve as the team matures

## See Also
- **quality-gates** — Gate criteria for phase transitions
- **review-checklists** — Code and design review criteria
- **quality-gates** — Quality criteria across phases
- **scrum-guide** — DoD in Scrum context
