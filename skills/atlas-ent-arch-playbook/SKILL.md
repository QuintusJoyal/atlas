---
name: atlas-ent-arch-playbook
description: Enterprise architecture playbook for atlas-ent-arch.
type: playbook
appliesTo: [atlas-ent-arch]
tags: [playbook, ent-arch, togaf, ddd]
---

# atlas-ent-arch

## Route
- enterprise architecture → ent-arch
- capability mapping → ent-arch
- integration patterns → ent-arch
- domain-driven design (strategic) → ent-arch
- platform redesign → ent-arch

## Knowledge
- TOGAF framework → k/pmbok-framework
- DDD strategic patterns → k/domain-driven-design
- Enterprise integration patterns → k/trade-off-analysis
- Trade-off analysis → k/trade-off-analysis

## Scope
enterprise architecture, capability mapping, integration patterns, DDD strategic design, platform strategy | NOT technical architecture (→ architect), cloud architecture (→ cloud), implementation (→ dev), data modeling (→ dba/data-eng)

## Delegation Examples
### Platform redesign
"Redesign platform for scale." → ent-arch + cloud in parallel: ent-arch defines logical architecture/integration patterns, cloud maps to infrastructure capabilities.

### Disconnected systems
"12 systems that don't talk to each other." → ent-arch: current-state capability map + integration gap analysis BEFORE proposing target architecture.
