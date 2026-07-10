---
name: test-design-techniques
load-when: Writing specific test cases, designing test inputs, covering edge cases
skip-when: Deciding test ratios (see testing-pyramid), formal classification (see istqb-test-levels)
---

# Test Design Techniques

## Quick Reference
- Equivalence partitioning: group similar inputs, test one from each group
- Boundary analysis: test at edges of input ranges, not middle
- State transitions: test state changes and invalid transitions
- Decision tables: test all combinations of conditions
- Error guessing: use experience to target likely defects

## Deep Dive

### Equivalence Partitioning
Divide inputs into groups where behavior is expected to be the same. Test one value from each group.

Example: age field (1-120)
- Valid: 25 (middle of valid range)
- Invalid low: -1 (below minimum)
- Invalid high: 121 (above maximum)
- Boundary: 1, 120 (edge values)

### Boundary Value Analysis
Defects cluster at boundaries. Test at, just below, and just above each boundary.

For range [1, 120]:
- Test: 0, 1, 2, 119, 120, 121
- Focus on: 0/1 boundary, 119/120 boundary

### State Transition Testing
Map all states and transitions. Test:
- Valid transitions (normal flow)
- Invalid transitions (should be rejected)
- Boundary states (initial, final, error states)

Example: order status
- Created → Processing → Shipped → Delivered
- Created → Cancelled (valid)
- Shipped → Created (invalid, should reject)

### Decision Tables
For complex business rules with multiple conditions:
| Condition | Rule 1 | Rule 2 | Rule 3 |
|-----------|--------|--------|--------|
| Has account | Y | Y | N |
| Is premium | Y | N | - |
| Discount | 20% | 10% | 0% |

Each column = one test case.

### Error Guessing
Use experience to target likely defects:
- Null/empty inputs
- Very large inputs
- Special characters in strings
- Concurrent access
- Network timeouts
- Resource exhaustion

### Combination Testing
For multiple input parameters, test combinations:
- All pairs: every pair of values tested at least once
- Each value: every value tested at least once
- Full combinatorial: all combinations (expensive, use for critical paths)

### Test Case Format
```markdown
| ID | Preconditions | Input | Expected | Priority |
|----|---------------|-------|----------|----------|
| TC01 | User logged in | Valid CSV upload | File processed | High |
| TC02 | User logged in | Empty file | Error message | Medium |
| TC03 | User not logged in | Valid CSV upload | Auth error | High |
```

## See Also
- **bdd-gherkin** — Given/When/Then for acceptance-level test design
- **testing-pyramid** — Where each technique applies in the pyramid
- **risk-based-testing** — Prioritizing which techniques to apply where
- **istqb-test-levels** — ISTQB framework for test design
