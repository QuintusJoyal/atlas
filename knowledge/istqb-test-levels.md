---
name: istqb-test-levels
load-when: Classifying tests by level, understanding ISTQB framework, formal test process
skip-when: Writing specific test cases (see test-design-techniques), deciding ratios (see testing-pyramid)
---

# ISTQB Test Levels

## Quick Reference
- Four levels: Component → Integration → System → Acceptance
- Each level has a specific scope and responsibility
- Defects found earlier are cheaper to fix
- Test process: plan → design → execute → evaluate → report
- Risk-based testing prioritizes high-risk areas first

## Deep Dive

### Test Levels (ISTQB Foundation)
| Level | Scope | Who Tests | What They Find |
|-------|-------|-----------|----------------|
| Component (Unit) | Single module/function | Developers | Logic errors, boundary bugs |
| Integration | Interfaces between modules | Developers + QA | Contract mismatches, data flow bugs |
| System | Complete system end-to-end | QA team | Functional errors, workflow bugs |
| Acceptance | Business requirements | stakeholders + QA | Requirements gaps, usability issues |

### Test Types
- **Functional**: Does it do what it should?
- **Non-functional**: Performance, security, usability, reliability
- **Regression**: Did new changes break existing functionality?
- **Smoke**: Quick sanity check before deeper testing
- **Localization**: Adaptation for different regions/languages

### Test Process (ISTQB)
1. **Planning**: scope, approach, resources, schedule
2. **Design**: test conditions, test cases, test data
3. **Execution**: run tests, record results
4. **Evaluation**: compare actual vs expected, assess completion criteria
5. **Reporting**: test summary, defect summary, recommendations

### Risk-Based Testing
- Identify risks (what could go wrong?)
- Assess probability and impact
- Prioritize testing on high-risk areas
- Allocate more test effort to critical paths
- Document risk acceptance decisions

### Traceability
Every test case should trace to:
- A requirement (what it verifies)
- A defect (what it found)
- A risk (what it mitigates)

Traceability matrices ensure coverage and identify gaps.

### Defect Life Cycle
New → Assigned → Open → Fix → Retest → Closed
                          ↓
                     Rejected / Deferred

### Exit Criteria
- All planned tests executed
- Defect density below threshold
- No open critical/blocker defects
- Coverage targets met
- Risk areas adequately tested

## See Also
- **testing-pyramid** — Practical ratios for component/integration/system
- **test-design-techniques** — How to design test cases at each level
- **risk-based-testing** — Deep dive on risk assessment and prioritization
- **quality-gates** — When each level is "done"
