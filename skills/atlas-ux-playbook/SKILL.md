---
name: atlas-ux-playbook
description: UX methodology for atlas-ux: user flows, accessibility, wireframes, and design tokens. Use when atlas-ux runs.
disable-model-invocation: true
---

# UX and UI playbook

Standards: WCAG 2.2 accessibility, Nielsen's 10 usability heuristics, design-token conventions. No Figma (rate limits).

## User flow
Map the steps from intent to outcome. Use mermaid for the flow.

## Wireframe (markdown)
Describe layout by region (header, content, actions) with hierarchy and states (empty, loading, error, success).

## Accessibility (WCAG)
Color contrast, keyboard navigation, focus order, labels and alt text, target size, motion safety.

## Heuristics check
Visibility of status, match to the real world, user control, consistency, error prevention, recognition over recall, flexibility, minimalist design, help users recover from errors, help and docs.

## Design tokens (in code)
Define color, spacing, type, and radius as named tokens so developers consume them directly.

## UX artifact
Flows, wireframes, accessibility notes, tokens. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/ux.md`.

## References
- https://www.w3.org/WAI/WCAG22/quickref/
- https://www.nngroup.com/articles/ten-usability-heuristics/
