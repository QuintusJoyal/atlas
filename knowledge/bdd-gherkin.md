---
name: bdd-gherkin
load-when: Writing acceptance tests, translating requirements to tests, creating feature files
skip-when: Writing unit tests (see test-driven-development), test ratios (see testing-pyramid)
---

# BDD / Gherkin

## Quick Reference
- Format: Feature → Scenario → Given/When/Then
- One scenario = one testable behavior
- Steps are reusable across scenarios via step definitions
- Feature files are living documentation, not just tests
- BDD bridges requirements (atlas-ba) and test automation (atlas-qa)

## Deep Dive

### Gherkin Syntax
```gherkin
Feature: CSV Export
  As a data analyst
  I want to export reports as CSV
  So I can analyze data in Excel

  Scenario: Export with data
    Given I have a report with 50 rows
    When I click "Export CSV"
    Then a CSV file downloads with 50 rows
    And the file has correct headers
```

### Structure Rules
- **Feature**: one sentence describing the capability
- **Scenario**: one testable behavior, not one test case
- **Given**: preconditions (state, data, configuration)
- **When**: the action being tested
- **Then**: expected outcome (assertions)
- **And/But**: continuation of the previous keyword

### Step Definitions
Each Gherkin step maps to code:
```gherkin
Given I have a report with 50 rows
```
Becomes a function that creates a report with 50 rows in the test database. Step definitions are reusable — one step can serve many scenarios.

### Scenario Outline
For data-driven tests:
```gherkin
Scenario Outline: Export formats
  Given I have a report
  When I export as <format>
  Then I get a <extension> file

  Examples:
    | format | extension |
    | CSV    | .csv      |
    | PDF    | .pdf      |
```

### Tags
```gherkin
@smoke @regression
Scenario: Login works
```
Tags control which scenarios run in which suites. Use `@smoke` for fast sanity checks, `@regression` for full suite.

### Common Mistakes
- Testing implementation details in Gherkin ("I click button X")
- Scenarios that depend on other scenarios
- Too many steps per scenario (>5 steps = split it)
- Vague Then steps ("it should work" is not testable)

### BDD Workflow
1. atlas-ba writes feature files with stakeholders
2. atlas-qa reviews for testability
3. atlas-dev implements step definitions
4. Feature files become living documentation
5. Changes to behavior = changes to feature files first

## See Also
- **test-driven-development** — Unit-level red-green-refactor
- **testing-pyramid** — How BDD scenarios fit the pyramid
- **istqb-test-levels** — Formal test classification
- **risk-based-testing** — Prioritizing which scenarios to write first
