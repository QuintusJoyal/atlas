---
name: review-checklists
load-when: Conducting code reviews, architecture reviews, design reviews
skip-when: Quality criteria (see quality-gates), completion criteria (see definition-of-done)
---

# Review Checklists

## Quick Reference
- Code review: correctness, clarity, consistency, complexity
- Architecture review: trade-offs, scalability, maintainability
- Design review: usability, accessibility, consistency
- Every review should check: does it meet DoD? does it match requirements?
- Focus on high-impact issues, not style nitpicks

## Deep Dive

### Code Review Checklist
```markdown
## Correctness
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Error handling is appropriate
- [ ] No security vulnerabilities

## Clarity
- [ ] Code is readable
- [ ] Names are meaningful
- [ ] Complex logic is commented
- [ ] Functions are small and focused

## Consistency
- [ ] Follows project style guide
- [ ] Matches existing patterns
- [ ] Uses established libraries

## Complexity
- [ ] No unnecessary complexity
- [ ] DRY (no duplication)
- [ ] Single responsibility per function/class
```

### Architecture Review Checklist
```markdown
## Design
- [ ] Meets requirements (functional and non-functional)
- [ ] Trade-offs are documented
- [ ] Simpler alternatives were considered
- [ ] Scalability requirements are clear

## Implementation
- [ ] Follows established patterns
- [ ] Uses standard libraries
- [ ] Avoids vendor lock-in
- [ ] Security controls are implemented

## Maintainability
- [ ] Code is organized and modular
- [ ] Documentation is adequate
- [ ] Tests are comprehensive
- [ ] Deployment is automated
```

### Design Review Checklist
```markdown
## Usability
- [ ] Follows Nielsen's heuristics
- [ ] Consistent with design system
- [ ] Error states are designed
- [ ] Empty states are designed

## Accessibility
- [ ] WCAG 2.1 AA compliant
- [ ] Keyboard accessible
- [ ] Screen reader tested
- [ ] Color contrast sufficient
```

### Review Best Practices
- Review in small batches (<400 lines)
- Focus on logic and design, not style
- Ask questions, don't make demands
- Approve with suggestions, not blocks
- Review within 24 hours

## See Also
- **quality-gates** — Quality criteria across phases
- **definition-of-done** — Completion criteria
- **clean-code-practices** — Code quality standards
- **wcag-2-1-checklist** — Accessibility requirements
