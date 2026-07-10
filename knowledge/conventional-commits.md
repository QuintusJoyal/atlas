---
name: conventional-commits
load-when: Writing commit messages, creating branches, versioning releases
skip-when: Code review (see review-checklists), code quality (see clean-code-practices)
---

# Conventional Commits

## Quick Reference
- Format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- Scope: optional, indicates the section of the codebase
- Description: imperative mood, lowercase, no period
- Breaking changes: add `!` after type or `BREAKING CHANGE:` in footer

## Deep Dive

### Commit Types
| Type | Description | Bumps |
|------|-------------|-------|
| feat | New feature | Minor |
| fix | Bug fix | Patch |
| docs | Documentation only | None |
| style | Formatting, no code change | None |
| refactor | Code change, no feature or fix | None |
| perf | Performance improvement | Patch |
| test | Adding or updating tests | None |
| build | Build system or dependencies | None |
| ci | CI configuration | None |
| chore | Maintenance tasks | None |
| revert | Reverts a previous commit | - |

### Examples
```
feat(auth): add OAuth2 login support
fix(api): handle null response from payment gateway
docs(readme): update installation instructions
refactor(db): extract connection pooling logic
perf(query): add index for user lookups
test(auth): add integration tests for login flow
feat(api)!: change response format for /users endpoint
```

### Breaking Changes
```markdown
feat(api)!: change response format for /users endpoint

BREAKING CHANGE: response now uses `{ data: [...] }` wrapper
instead of flat array. Clients must update response parsing.
```

### Branch Naming
```
feat/oauth2-login
fix/payment-timeout
docs/readme-update
chore/dependency-bump
```

### Semantic Versioning
- MAJOR: breaking changes
- MINOR: new features (backward compatible)
- PATCH: bug fixes (backward compatible)

## See Also
- **clean-code-practices** — Clean commit messages reflect clean code
- **review-checklists** — Reviewing commit quality
- **pmbok-framework** — Release management practices
- **quality-gates** — Automated checks including commit validation
