---
name: engineering-standards
description: Engineering standards for code, commits, branches, secrets, and tests.
load: contextual
globs: "**/*.{ts,tsx,js,jsx,py,go,rs,java,kt,rb,php,cs,cpp,c,h,hpp,scala,swift,sql,sh,ps1,yaml,yml}"
---

# Engineering standards

Applies when editing source. Keep it simple, tested, and secure.

## Code
- Follow SOLID and clean-code principles. Small, focused functions. Clear names.
- Prefer existing libraries and patterns in the repo over new ones. Match the surrounding style.
- No meta comments. Comment only non-obvious intent, trade-offs, or constraints.
- Handle errors explicitly. No silent failures.

## Secrets and safety
- Never hardcode secrets, tokens, or credentials. Read from environment or a secrets manager.
- Never commit secrets or PII. Validate and sanitize external input.

## Tests
- New logic needs tests. Follow the test pyramid: many unit, fewer integration, few end-to-end.
- A change is not done until its tests pass.

## Version control
- Conventional commits: `type(scope): summary` (feat, fix, docs, refactor, test, chore).
- Branch naming: `type/short-description` (for example `feat/user-auth`, `fix/login-redirect`).
- Keep commits focused and reviewable. Write commit and MR text in the human-authored voice (`writing-style.md`).
- Opening or merging an MR, or pushing through an MCP, is a write action that needs user approval.

## Lite mode

Generated into `lite/rules/engineering-standards.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# Engineering Standards (Lite)

When editing source code:

1. Follow SOLID and clean-code principles. Small functions. Clear names.
2. Match the existing code style in the repo.
3. Handle errors explicitly. No silent failures.
4. New logic needs tests. Tests must pass before delivery.
5. No hardcoded secrets. Use environment variables.
6. Conventional commits: `type(scope): summary`.
<!-- lite:end -->
