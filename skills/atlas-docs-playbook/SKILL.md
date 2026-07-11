---
name: atlas-docs-playbook
description: Documentation playbook for atlas-docs.
type: playbook
appliesTo: [atlas-docs]
tags: [playbook, docs, diataxis]
---

# atlas-docs

## Route
- user documentation → docs
- API documentation → docs
- changelog updates → docs
- runbooks → docs
- writing-style review → docs

## Knowledge
- Diataxis framework (tutorials/how-to/reference/explanation) → inline knowledge
- Clean code (documentation section) → k/clean-code-practices
- Conventional commits (for changelogs) → k/conventional-commits

## Scope
tutorials, how-to guides, reference docs, explanations, changelogs, runbooks, writing-style enforcement | NOT implementation (→ dev), architecture docs (→ architect), test docs (→ qa), deployment docs (→ devops)

## Delegation Examples
### Feature documentation
"New feature shipped." → docs: update changelog (user-facing descriptions), update API docs, create/update runbook if operational procedures changed.

### Missing runbook
"Production incident revealed no runbook." → docs: interview maintenance for investigation steps, extract resolution procedure, create runbook with trigger/checklist/escalation.

### Documentation audit
"Docs are outdated." → docs: audit against Diataxis (tutorial/how-to/reference/explanation), identify gaps, prioritize updates.
