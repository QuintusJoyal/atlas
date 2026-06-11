---
name: atlas-ba-playbook
description: Business analysis methodology for atlas-ba: elicitation, edge cases, BDD, and data flows. Use when atlas-ba runs.
disable-model-invocation: true
---

# Business analyst playbook

Standards: BABOK elicitation techniques, BDD (Gherkin), acceptance-criteria patterns.

## Elicitation
Interviews, document analysis, observation, and workshops. Capture assumptions explicitly and mark each for confirmation.

## Edge-case matrix
For each input or flow, list normal, boundary, invalid, and failure cases with the expected behavior.

| Case | Input | Expected | Notes |
| --- | --- | --- | --- |

## BDD scenarios
```
Scenario: <name>
  Given <context>
  When <action>
  Then <outcome>
```

## Data and process flows
Describe inputs, transformations, outputs, and ownership. Use mermaid for flows.

## Analysis artifact
Refined requirements, edge-case matrix, BDD scenarios, data flows, assumptions to confirm. Persist to `.atlas/runs/<run-id>/analysis.md`. Raise requirement gaps to the user immediately.

## References
- https://www.iiba.org/business-analysis-standards/babok-guide/
- https://cucumber.io/docs/gherkin/
