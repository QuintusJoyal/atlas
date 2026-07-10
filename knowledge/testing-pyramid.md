---
name: testing-pyramid
load-when: Deciding test ratios, diagnosing test suite balance, reviewing coverage strategy
skip-when: Writing specific test cases (see test-design-techniques), formal test classification (see istqb-test-levels)
---

# Test Pyramid

## Quick Reference
- Ratio: Unit 70% | Integration 20% | E2E 10%
- Never skip unit tests to write more E2E
- One assertion per concept, not per line
- Unit = fast, deterministic | Integration = contracts | E2E = user flows
- Inverted pyramid = maintenance debt

## Deep Dive

### Why the Pyramid Shape
Unit tests are cheap, fast, and deterministic. They catch logic errors at the lowest cost. Integration tests verify contracts between components — they're slower but catch interface bugs. E2E tests verify complete user flows — they're expensive, slow, and brittle. The ratio reflects cost and reliability at each level.

### When to Invert
Legacy codebases sometimes start with E2E and work downward. This is acceptable temporarily. Plan to rebalance by extracting unit-testable logic from E2E flows. Track the inversion ratio and set a target date to rebalance.

### The Ice Cream Cone Anti-Pattern
All E2E, no unit or integration tests. Symptoms: slow test suite, flaky tests, long feedback loops, developers avoiding tests. Fix: extract business logic into unit-testable functions, add integration tests for API contracts.

### Cost Per Level
| Level | Speed | Cost | Reliability | Maintenance |
|-------|-------|------|-------------|-------------|
| Unit | ms | Low | High | Low |
| Integration | seconds | Medium | Medium | Medium |
| E2E | minutes | High | Low | High |

### Coverage Targets
- Unit: >80% line coverage on business logic
- Integration: >60% on API contracts and data flows
- E2E: cover critical user paths only (login, checkout, core workflows)

### Test Isolation
Each test must be independent. No shared state between tests. No order dependency. Tests that depend on other tests are integration tests disguised as unit tests.

## See Also
- **test-driven-development** — Red-green-refactor cycle, writing tests first
- **test-design-techniques** — Equivalence partitioning, boundary analysis
- **testing-anti-patterns** — Flaky tests, coverage gaming, inverted pyramid
- **quality** — Definition of done, review checklists
- **istqb-test-levels** — Formal test classification, ISTQB syllabus
