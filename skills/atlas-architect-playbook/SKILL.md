---
name: atlas-architect-playbook
description: Architecture methodology for atlas-architect: C4, ADRs, NFRs, and trade-off tables. Use when atlas-architect runs.
disable-model-invocation: true
---

# Software architect playbook

Standards: C4 model, 12-Factor App, cloud well-architected pillars, ADR conventions.

## C4 (use what helps)
Context, Container, Component. Diagram in mermaid. Skip levels that add no clarity.

## Architecture Decision Record
```
# ADR <n>: <title>
Status: proposed | accepted | superseded
Context: <forces and constraints>
Decision: <what and why>
Consequences: <trade-offs, follow-ups>
```

## Non-functional requirements
Performance, scalability, availability, security, cost, maintainability, observability. State targets, not adjectives.

## Trade-off table
| Option | Pros | Cons | Cost | Decision |
| --- | --- | --- | --- | --- |

## Simplicity check
Prefer existing components and proven patterns. Each new abstraction must justify its complexity and its future scaling benefit.

## Design artifact
Component design, ADRs, NFRs, trade-offs, risks. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/design.md`. Feeds the design gate.

## References
- https://c4model.com/
- https://12factor.net/
- https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
