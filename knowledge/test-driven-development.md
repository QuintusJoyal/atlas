---
name: test-driven-development
load-when: Writing tests first, implementing new features, refactoring with safety net
skip-when: Test ratios (see testing-pyramid), BDD acceptance tests (see bdd-gherkin)
---

# Test-Driven Development (TDD)

## Quick Reference
- Red: write a failing test
- Green: write the minimum code to pass
- Refactor: clean up while tests pass
- One test at a time
- Tests are a design tool, not just verification
- Every bug gets a test before the fix

## Deep Dive

### The TDD Cycle
1. **Red**: write a test for the next small behavior. Watch it fail.
2. **Green**: write the simplest code that makes it pass.
3. **Refactor**: improve the code while keeping tests green.

### Why TDD Works
- **Design feedback**: test-first forces you to think about the API before implementation
- **Regression safety**: every bug becomes a test
- **Documentation**: tests show how the code is intended to be used
- **Small steps**: prevents big-bang integration issues

### TDD Rules
1. Never write production code without a failing test
2. Write the smallest test that fails
3. Write the smallest code that passes
4. Refactor only when all tests are green
5. One test, one behavior

### Triangulation
When unsure about implementation:
1. Write test for known case
2. Write test for second case
3. Refactor to generalize

### Mocking
- Mock external dependencies (databases, APIs, file systems)
- Don't mock value objects
- Prefer real objects when they're fast and deterministic
- Mock at boundaries, not throughout

### When to Break TDD
- Exploratory spikes (throw away the code afterward)
- UI prototyping (add tests before shipping)
- Performance optimization (measure, then add tests for the optimization)

### TDD vs Test-First
TDD = test-first + small steps + refactoring. Writing tests first without the cycle is just test-first, not TDD.

## See Also
- **testing-pyramid** — How TDD fits the test pyramid
- **clean-code-practices** — TDD produces clean code naturally
- **solid-principles** — TDD naturally enforces SOLID
- **refactoring-patterns** — The refactor step in TDD
