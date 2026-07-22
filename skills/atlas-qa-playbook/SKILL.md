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
- "definition of done" → k/quality-gates
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

## Lite mode

Generated into `lite/skills/atlas-qa-playbook/SKILL.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# atlas-qa (Lite Playbook)

## Route
- write tests → atlas-qa
- verify fix → atlas-qa
- regression test → atlas-qa
- quality assessment → atlas-qa

## Rules
1. Test against requirements, not against the implementation.
2. Report with evidence: steps, expected, actual.
3. Never approve with failing tests or critical findings.

## Knowledge (inlined, no external files)
- Testing pyramid: ratio unit 70% / integration 20% / e2e 10%. Never skip unit tests to write more e2e. Inverted pyramid = maintenance debt.
- Test design: equivalence partitioning (test one value per input group), boundary analysis (test at edges, not the middle), decision tables (all combinations of conditions), error guessing (target likely defects from experience).
- BDD/Gherkin: Feature → Scenario → Given/When/Then. One scenario = one testable behavior. Feature files are living documentation, not just tests.
<!-- lite:end -->
