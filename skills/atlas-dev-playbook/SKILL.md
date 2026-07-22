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

## Lite mode

Generated into `lite/skills/atlas-dev-playbook/SKILL.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# atlas-dev (Lite Playbook)

## Route
- implement feature → atlas-dev
- fix bug → atlas-dev
- refactor code → atlas-dev
- write tests → atlas-dev

## Rules
1. Read before edit. Run tests before claiming done.
2. Follow existing code style. Match the surrounding patterns.
3. Handle errors explicitly. No silent failures.

## Knowledge (inlined, no external files)
- Clean code: meaningful names, functions do one thing (<20 lines, 0-3 args), comments explain why not what, use exceptions not null returns.
- SOLID: one class = one reason to change; open for extension, closed for modification; subtypes must be substitutable; small specific interfaces beat one general one; depend on abstractions not concretions.
- TDD: red (write a failing test) → green (minimum code to pass) → refactor (clean up while green). One test at a time. Every bug gets a test before the fix.
<!-- lite:end -->
