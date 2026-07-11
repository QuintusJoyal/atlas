---
name: quality-gates
load-when: Defining phase transitions, setting pass/fail criteria, release readiness
skip-when: Completion criteria (see definition-of-done), review criteria (see review-checklists)
---

# Quality Gates

## Quick Reference
- Gate: a checkpoint that must pass before proceeding to next phase
- Each gate has explicit pass/fail criteria
- Gates prevent quality degradation across phases
- Automate gates when possible (CI/CD checks)
- Document gate decisions and exceptions
- Variant-aware: small variants skip requirements and design gates

## Deep Dive

### Variant-aware gates
- **small variant:** only the final gate is enforced. Requirements and design gates are skipped. Final gate auto-approved if all DoD items pass.
- **full variant:** all gates are enforced as listed below. User approves all gates.
- **Injected phases:** phases added via conditions follow the same gate rules as native phases.

### Auto-approve criteria (small variant)
Small variant final gate is auto-approved when all DoD items pass. For small variant, DoD is implicit: role completed = gate passed. No explicit DoD checklist validation needed. Lead trusts the role's handoff.

If handoff has `[USER]` items or open questions → pause for user input instead of auto-approving.

### Common Gates
| Gate | Phase Transition | Key Criteria | Variant | Auto-approve |
|------|-----------------|--------------|---------|--------------|
| Requirements Gate | Requirements → Design | Requirements approved, acceptance criteria defined, stakeholder sign-off | full only | no |
| Design Gate | Design → Implementation | Architecture reviewed, trade-offs documented, security assessed | full only | no |
| Code Gate | Implementation → Testing | Code reviewed, unit tests passing, no critical issues | both | small: auto (role completed), full: user |
| Test Gate | Testing → Deployment | All tests passing, coverage targets met, no open P0/P1 bugs | both | small: auto (role completed), full: user |
| Release Gate | Deployment → Production | Staging validated, rollback plan ready, monitoring configured | both | small: auto (role completed), full: user |

### Gate Criteria Template
```markdown
## Requirements Gate
### Must Pass
- [ ] All user stories have acceptance criteria
- [ ] Edge cases identified
- [ ] Non-functional requirements documented
- [ ] Stakeholder approval obtained

### Should Pass
- [ ] BDD scenarios written
- [ ] Risk assessment completed
- [ ] Dependencies identified
```

### Automated Gates (CI/CD)
- Build passes
- All tests pass
- Code coverage >= threshold
- No critical security findings
- Linting passes
- Type checking passes

### Gate Exceptions
- Emergency fixes may skip gates (with explicit approval)
- Document which gate was skipped and why
- Track exception metrics
- Review exceptions in retrospectives

## See Also
- **definition-of-done** — Work item completion criteria
- **review-checklists** — Review criteria for gates
- **quality-gates** — (this file) — Quality criteria across phases
- **pmbok-framework** — Phase gate management
