---
name: atlas-dev-playbook
description: Engineering methodology for atlas-dev: clean code, TDD workflow, and commit and branch conventions. Use when atlas-dev runs.
disable-model-invocation: true
---

# Software engineer playbook

Standards: SOLID, clean code, conventional commits, test-driven development. The `engineering-standards.mdc` rule also applies.

## TDD workflow
1. Write a failing test for the next small behavior.
2. Make it pass with the simplest code.
3. Refactor while green.
Repeat. Keep changes small and reviewable.

## Clean code
Small focused functions, clear names, explicit error handling, no dead code, no meta comments.

## Reuse first
Check the repo and standard libraries before writing custom code. Match existing patterns.

## Commits and branches
- Commit: `type(scope): summary` (feat, fix, docs, refactor, test, chore).
- Branch: `type/short-description`.
- Write commit and MR text in the human-authored voice. No em dashes.

## Implementation artifact
Summary, files changed, tests added, deviations from design. Persist to `.atlas/runs/<run-id>/implementation.md`. MR or push via MCP needs user approval.

## References
- https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- https://www.conventionalcommits.org/
