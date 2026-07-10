---
name: atlas-pm-playbook
description: Product management methodology for atlas-pm: user stories, acceptance criteria, prioritization, and definition of ready. Use when atlas-pm runs.
disable-model-invocation: true
---

# Product manager playbook

Standards: INVEST for stories, Scrum and agile delivery, user-story mapping, RICE and MoSCoW for prioritization.

## User story (INVEST)
Independent, Negotiable, Valuable, Estimable, Small, Testable.

```
As a <user>, I want <capability> so that <benefit>.
```

## Acceptance criteria
Write testable criteria in given-when-then or a checklist. Each must be verifiable by atlas-qa.

## Prioritization
- RICE: Reach x Impact x Confidence / Effort.
- MoSCoW: Must, Should, Could, Won't (this cycle).

## Definition of ready (requirements gate)
- [ ] Problem and target user are clear
- [ ] Stories follow INVEST
- [ ] Acceptance criteria are testable
- [ ] Scope and out-of-scope stated
- [ ] Open questions raised to the user
- [ ] Priority assigned

## Requirements artifact
Problem statement, stories, acceptance criteria, scope, priority, open questions. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/requirements.md`.

## References
- https://www.agilealliance.org/glossary/invest/
- https://www.scrum.org/resources/what-is-scrum
