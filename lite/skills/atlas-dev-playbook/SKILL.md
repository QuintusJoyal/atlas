<!-- GENERATED FILE. Do not edit directly.
     Source: skills/atlas-dev-playbook/SKILL.md (the <!-- lite:start --> block).
     Regenerate with: python3 scripts/build-lite.py -->

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
