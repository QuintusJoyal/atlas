---
name: atlas-qa-playbook
description: QA methodology for atlas-qa: test pyramid, test plans, coverage, and bug reports. Use when atlas-qa runs.
disable-model-invocation: true
---

# QA engineer playbook

Standards: ISTQB fundamentals, the test pyramid, risk-based testing.

## Test pyramid
Many unit tests, fewer integration tests, few end-to-end tests. Push coverage down the pyramid.

## Test plan
Tie every test to an acceptance criterion. Cover normal, boundary, invalid, and failure paths. Note risk areas first (risk-based testing).

## Bug report
```
Title: <concise summary>
Severity: blocker | critical | major | minor
Steps to reproduce: 1... 2... 3...
Expected: <...>
Actual: <...>
Environment: <...>
```

## Smoke tests
For UI, drive critical paths through a browser MCP if connected. Confirm the happy path before deeper testing.

## Test artifact
Test plan, automated tests, results, bug reports. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/test-plan.md`. Feeds the security and final gates.

## References
- https://www.istqb.org/
- https://martinfowler.com/articles/practical-test-pyramid.html
