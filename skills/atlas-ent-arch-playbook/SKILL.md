---
name: atlas-ent-arch-playbook
description: Enterprise architecture methodology for atlas-ent-arch: TOGAF, integration patterns, and capability mapping. Use when atlas-ent-arch runs.
disable-model-invocation: true
---

# Enterprise and solution architect playbook

Standards: TOGAF, enterprise integration patterns, domain-driven design, capability mapping.

## Approach
Start from business capabilities and outcomes. Map current and target state. Identify gaps and a phased path.

## Integration
Choose integration styles deliberately (events, APIs, batch). Define contracts and ownership. Avoid point-to-point sprawl.

## Domain-driven design
Bounded contexts, clear ownership, and a shared language. Align services to domains.

## Capability map
List capabilities, the systems that serve them, and gaps or overlaps.

## Enterprise-architecture artifact
Target design, integration approach, capability map, trade-offs. Persist to `.atlas/runs/<run-id>/ent-arch.md`. Diagrams in mermaid.

## References
- https://www.opengroup.org/togaf
- https://www.enterpriseintegrationpatterns.com/
