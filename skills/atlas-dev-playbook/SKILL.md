---
name: atlas-dev-playbook
description: Engineering playbook for atlas-dev.
type: playbook
appliesTo: [atlas-dev]
tags: [playbook, dev, tdd, clean-code]
---

# atlas-dev

## Route
- feature implementation → dev
- bug fixes → dev
- refactoring → dev
- code review (implementation) → dev
- integration work → dev

## Knowledge
- TDD red-green-refactor → k/test-driven-development
- SOLID principles → k/solid-principles
- Clean code practices → k/clean-code-practices
- Refactoring patterns → k/refactoring-patterns
- Conventional commits → k/conventional-commits
- Anti-patterns to avoid → k/anti-patterns

## Scope
implementation, TDD, code quality, commits, branches, refactoring, integration | NOT test strategy (→ qa), architecture decisions (→ architect), deployment (→ devops), security controls (→ security)

## Delegation Examples
### Feature implementation
"Implement CSV export endpoint." → dev: TDD workflow (red-green-refactor), conventional commits, implementation summary with files changed and tests added.

### Bug fix
"Fix 500 error on checkout." → dev: reproduce first, identify root cause, write failing test, fix, verify. Implementation artifact with root cause and fix summary.

### Refactoring
"Extract shared validation logic." → dev: identify code smells, apply refactoring patterns, verify tests pass, conventional commit.
