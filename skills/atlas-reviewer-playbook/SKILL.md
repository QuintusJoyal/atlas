---
name: atlas-reviewer-playbook
description: Code review playbook for atlas-reviewer.
type: playbook
appliesTo: [atlas-reviewer]
tags: [playbook, review, quality]
---

# atlas-reviewer

## Route
- code review → reviewer
- architecture review → reviewer
- design review → reviewer
- quality gate → reviewer
- writing-style review → reviewer

## Knowledge
- Review checklist → k/review-checklists
- Clean code practices → k/clean-code-practices
- SOLID principles → k/solid-principles
- Conventional commits → k/conventional-commits
- Definition of done → k/definition-of-done
- Quality gates → k/quality-gates

## Scope
code review, architecture review, design review, quality gate, charter conformance, writing-style review | NOT implementation (→ dev), security audit (→ security), testing (→ qa), deployment (→ devops)

## Delegation Examples
### Standard code review
"PR ready for review." → reviewer: correctness, edge cases, tests, simplicity, patterns, human voice. Findings grouped by severity: blocker/suggestion/nit.

### Documentation review
"Docs-only changes." → reviewer: writing-style rules, em dashes, AI tells, technical accuracy, Diataxis alignment.

### Quality gate
"Pre-merge review." → reviewer: review diff, verify charter conformance, apply writing-style, check security findings addressed, approve/request-changes.
