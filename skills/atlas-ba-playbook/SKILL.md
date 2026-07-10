---
name: atlas-ba-playbook
description: Business analysis playbook for atlas-ba.
type: playbook
appliesTo: [atlas-ba]
tags: [playbook, ba, elicitation, bdd]
---

# atlas-ba

## Route
- requirements analysis → ba
- edge cases, gap analysis → ba
- BDD scenarios → ba
- data flows, process maps → ba
- stakeholder interviews → ba

## Knowledge
- BABOK elicitation techniques → k/babok-techniques
- BDD/Gherkin syntax → k/bdd-gherkin
- SPIN questioning → k/spin-selling
- MECE problem decomposition → k/mece-framework

## Scope
requirements analysis, edge-case matrices, BDD scenarios, data flows, process maps, gap analysis | NOT project management (→ pm), implementation (→ dev), testing (→ qa), architecture (→ architect)

## Delegation Examples
### Requirements refinement
"PRD from pm needs analysis." → ba: build edge-case matrix, write BDD scenarios, produce data flow diagrams. Gate: analysis gates architect design.

### Contradictory requirements
"Requirements conflict (speed vs accuracy)." → ba: document contradiction, map trade-offs as decision table, flag to architect + pm for resolution.

### Edge-case discovery
"Complex form with conditional fields." → ba: list all input combinations, expected behaviors, validation rules per state.
