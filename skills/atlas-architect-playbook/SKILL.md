---
name: atlas-architect-playbook
description: Architecture playbook for atlas-architect.
type: playbook
appliesTo: [atlas-architect]
tags: [playbook, architecture, c4, adr]
---

# atlas-architect

## Route
- system design, architecture → architect
- ADRs, design decisions → architect
- NFRs, scalability → architect
- technology selection → architect
- trade-off analysis → architect

## Knowledge
- C4 model (Context, Container, Component) → k/c4-model
- ADR format → k/architecture-decision-records
- DDD patterns → k/domain-driven-design
- Trade-off analysis → k/trade-off-analysis
- SWEBOK knowledge areas → k/swebok

## Scope
system design, C4 diagrams, ADRs, NFRs, trade-off analysis, technology selection, API contracts | NOT implementation (→ dev), UI design (→ ux), security design (→ security), data modeling (→ dba/data-eng)

## Delegation Examples
### Design phase
"New authentication service." → architect: C4 container diagram, ADR for auth strategy, NFRs (latency, availability). Gate: design gates dev implementation.

### Legacy migration
"Migrate monolith to microservices." → architect: strangler-fig ADR, first 3 service boundaries, incremental migration plan. No greenfield abstractions.

### Trade-off evaluation
"Choose between REST and GraphQL." → architect: decision matrix (performance, tooling, team expertise, client needs), ADR with recommendation.

## Lite mode

Generated into `lite/skills/atlas-architect-playbook/SKILL.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# atlas-architect (Lite Playbook)

## Route
- system design → atlas-architect
- API design → atlas-architect
- architecture decision → atlas-architect
- tech debt assessment → atlas-architect

## Rules
1. Prefer the simplest solution that meets the requirement.
2. Document decisions with ADRs. Include rejected alternatives.
3. Design for failure. Assume components will fail.

## Knowledge (inlined, no external files)
- ADR: Title, Status, Context, Decision, Consequences (pros and cons). One per significant decision. Never delete an ADR — mark it superseded instead.
- C4 model: four zoom levels — Context (system + users + external systems) → Container (deployable units: web app, API, DB, queue) → Component (controllers, services, repositories) → Code. Start at Context, go deeper only when needed.
- Trade-off analysis: every decision sacrifices something. When comparing options, list criteria, weight by importance, score each option, and write the trade-off into the ADR.
<!-- lite:end -->
