---
name: atlas-qa-playbook
description: QA playbook for atlas-qa.
type: playbook
appliesTo: [atlas-qa]
tags: [playbook, qa, testing]
---

# atlas-qa

## Route
- test strategy, test plans → qa
- automated test writing → qa
- bug triage, bug reports → qa
- regression testing → qa
- coverage analysis → qa
- smoke testing → qa

## Knowledge
- 70/20/10 unit/integration/e2e → k/testing-pyramid
- "red-green-refactor" → k/test-driven-development
- "equivalence"/"boundary" → k/test-design-techniques
- "definition of done" → k/quality-bars
- "flaky"/"inverted pyramid" → k/anti-patterns
- BDD/Gherkin → k/bdd-gherkin
- ISTQB levels → k/istqb-test-levels
- Risk-based testing → k/risk-based-testing

## Scope
test strategy, test plans, automated tests, bug reports, coverage analysis, smoke tests, regression testing | NOT implementation (→ dev), infrastructure (→ devops), security controls (→ security), requirements (→ pm/ba)

## Delegation Examples
### Test plan creation
"Write tests for CSV export endpoint." → qa: test plan with unit/integration/e2e coverage, risk-based prioritization. Gate: tests pass, coverage targets met.

### Bug investigation
"Users reporting 500 errors on checkout." → qa: run existing tests first, then edge-case tests for concurrent checkout, expired sessions, gateway timeout.

### Pre-release validation
"Release candidate ready." → qa: full smoke suite against staging, regression testing scoped to auth/payments/exports, readiness report with pass/fail per risk area.
