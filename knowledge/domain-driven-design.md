---
name: domain-driven-design
load-when: Modeling complex domains, defining bounded contexts, designing aggregates
skip-when: Simple CRUD apps, architecture diagrams (see c4-model), decision records (see architecture-decision-records)
---

# Domain-Driven Design (DDD)

## Quick Reference
- Ubiquitous language: team and domain experts share the same vocabulary
- Bounded context: explicit boundary where a model applies
- Aggregate: cluster of entities with a root and consistent invariants
- Domain event: something that happened in the domain
- Strategic design: context maps, relationships between bounded contexts

## Deep Dive

### Strategic Design
**Bounded Context**: a boundary within which a particular domain model is defined. Different contexts may have different models for the same concept (e.g., "Customer" in Sales vs Support).

**Context Map**: shows relationships between bounded contexts.
- Partnership: teams coordinate closely
- Customer-Supplier: one depends on the other
- Conformist: one conforms to the other's model
- Anti-Corruption Layer: translation layer between contexts

### Tactical Design
**Entity**: object with identity that persists over time.
**Value Object**: immutable object defined by its attributes (no identity).
**Aggregate**: cluster of entities with a root entity (aggregate root) that enforces invariants.
**Domain Event**: record of something significant that happened.
**Domain Service**: operation that doesn't belong to any entity.

### Aggregate Rules
- Reference other aggregates by identity only (not by object reference)
- One transaction per aggregate
- Aggregate root controls all invariants
- Keep aggregates small

### Bounded Context Patterns
- **Core**: your competitive advantage, invest heavily
- **Supporting**: needed but not differentiating, build or buy
- **Generic**: commodity, buy off-the-shelf

### When to Use DDD
- Complex business logic with rich domain rules
- Multiple teams working on different parts of the system
- Long-lived projects where domain understanding evolves
- Microservices (bounded contexts map well to services)

### When NOT to Use DDD
- Simple CRUD applications
- Short-lived projects
- Domain is well-understood and stable

## See Also
- **c4-model** — Visualizing bounded contexts and containers
- **architecture-decision-records** — Documenting DDD decisions
- **trade-off-analysis** — When DDD is overkill vs when it's essential
- **swebok** — Software engineering knowledge areas
