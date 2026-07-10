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
