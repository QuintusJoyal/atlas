---
name: atlas-ux-playbook
description: UX playbook for atlas-ux.
type: playbook
appliesTo: [atlas-ux]
tags: [playbook, ux, wcag, wireframes]
---

# atlas-ux

## Route
- user flows, wireframes → ux
- accessibility review → ux
- design tokens → ux
- usability concerns → ux
- interaction patterns → ux

## Knowledge
- WCAG 2.1 checklist → k/wcag-2-1-checklist
- Nielsen's 10 heuristics → k/nielsen-heuristics
- Material Design patterns → k/material-design-principles
- BDD scenarios (for user flows) → k/bdd-gherkin

## Scope
user flows, wireframes, accessibility, design tokens, interaction patterns, usability heuristics | NOT implementation (→ dev), backend design (→ architect), requirements (→ pm/ba), security (→ security)

## Delegation Examples
### New feature design
"Redesign checkout flow." → ux: user flow diagram, wireframes for each state (empty, loading, error, success), accessibility notes, design tokens.

### Accessibility audit
"Check accessibility of existing UI." → ux: WCAG 2.1 AA audit, contrast checks, keyboard navigation, screen reader testing recommendations.

### Constraint-driven design
"Complex form with conditional fields." → ux: map every visibility combination as decision table, wireframe each unique layout state, flag states with >3 visible fields.
