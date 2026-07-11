---
name: architectural-governance
description: Architecture governance: review boards, tech debt tracking, standards compliance. Load when architecture decisions or reviews are in motion.
load: on-demand
---

# Architectural governance

Architecture decisions outlive the code they produce. Govern them deliberately.

## Decision records
- Every significant architectural decision gets an ADR (Architecture Decision Record).
- Format: Title, Status, Context, Decision, Consequences, Alternatives considered.
- Store ADRs in `docs/adr/` in the codebase. Never edit an accepted ADR; supersede it with a new one.
- Reference: `k/architecture-decision-records.md`.

## Review process
- Architectural changes require review by atlas-architect or atlas-ent-arch before implementation.
- Review scope: scalability, security, operability, cost impact, alignment with existing architecture.
- Document review outcomes in the ADR or design document.

## Standards compliance
- All designs must comply with established patterns and standards in the codebase.
- Deviations require explicit justification documented in the ADR.
- Reference: `k/solid-principles.md`, `k/clean-code-practices.md`.

## Tech debt management
- Track tech debt explicitly: create issues with a `tech-debt` label.
- Categorize debt: deliberate (known trade-off) vs accidental (poor practice).
- Allocate capacity for debt reduction every sprint or cycle.

## Complexity budget
- Before adding abstraction, justify it: will it reduce complexity or move it?
- Prefer the simplest solution that meets the requirement.
- Flag when complexity is growing faster than capability.

## Architecture fitness functions
- Define measurable criteria for architectural health: test coverage, dependency count, build time, coupling metrics.
- Run fitness functions in CI. Fail the build when criteria are violated.
- Reference: `k/aws-well-architected.md`, `k/azure-well-architected.md`.
