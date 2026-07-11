---
name: risk-based-testing
load-when: Prioritizing tests, allocating test effort, assessing test coverage gaps
skip-when: Writing specific test cases (see test-design-techniques), test ratios (see testing-pyramid)
---

# Risk-Based Testing

## Quick Reference
- Test what matters most first
- Risk = probability × impact
- High-risk areas get more test effort, more test types, deeper coverage
- Document risk decisions for accountability
- Reassess risks as the project evolves

## Deep Dive

### What Is Risk-Based Testing
Instead of testing everything equally, focus testing effort on areas most likely to fail and most costly if they do. This is essential when time and resources are limited.

### Risk Assessment Matrix
| | Low Impact | Medium Impact | High Impact |
|---|---|---|---|
| **High Probability** | Medium risk | High risk | Critical risk |
| **Medium Probability** | Low risk | Medium risk | High risk |
| **Low Probability** | Minimal | Low risk | Medium risk |

### How to Identify Risks
- **Code complexity**: complex logic = higher defect probability
- **Change frequency**: frequently changed code = higher regression risk
- **Integration points**: external APIs, databases, third-party services
- **Business criticality**: revenue-impacting, compliance-required, user-facing
- **Historical defects**: areas with past bugs likely have more

### Risk Mitigation Through Testing
| Risk Level | Test Approach |
|------------|---------------|
| Critical | Unit + integration + E2E + exploratory + performance |
| High | Unit + integration + targeted E2E |
| Medium | Unit + integration |
| Low | Unit tests only |

### Risk Register Format
```markdown
| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| Payment gateway timeout | Medium | High | Integration test + retry logic test | atlas-qa |
| CSV encoding issues | High | Low | Unit tests for charset handling | atlas-dev |
```

### When to Reassess Risks
- After major design changes
- After production incidents
- When new integration points are added
- When timeline or scope changes significantly

### Coverage vs Risk Alignment
Map test coverage to risk areas. If high-risk areas have low coverage, that's a gap. If low-risk areas have high coverage, that's over-investment.

## See Also
- **testing-pyramid** — How risk informs the ratio of test levels
- **test-design-techniques** — Designing tests for high-risk areas
- **quality-gates** — Risk-based exit criteria
- **anti-patterns** — Testing low-risk areas while ignoring high-risk
