---
name: atlas-reviewer-playbook
description: Review methodology for atlas-reviewer: checklist, charter conformance, and feedback. Use when atlas-reviewer runs.
disable-model-invocation: true
---

# Code reviewer playbook

Standards: established engineering review practices. Read only: recommend, do not apply.

## Review checklist
- [ ] Correct and handles edge cases
- [ ] Tests cover the change and pass
- [ ] Simple; no needless complexity or abstraction
- [ ] Reuses existing patterns and libraries
- [ ] Errors handled explicitly; no secrets
- [ ] Names and structure are clear; no meta comments
- [ ] Charter conformance: simplicity, best practices
- [ ] Human-authored voice: no em dashes or AI tells in comments, docs, commit text

## Feedback format
Group by severity: blocker, suggestion, nit. Each item gets a concrete, actionable change. Be specific and kind.

## Review artifact
Findings grouped by severity with suggestions, plus a pass or block recommendation. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/review.md`.

## References
- https://google.github.io/eng-practices/review/
