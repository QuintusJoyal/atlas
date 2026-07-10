---
name: atlas-maintenance-playbook
description: Maintenance methodology for atlas-maintenance: triage, debugging, regressions, and postmortems. Use when atlas-maintenance runs.
disable-model-invocation: true
---

# Maintenance and support playbook

Standards: SRE incident and postmortem practice, structured triage, systematic debugging.

## Triage
Assess impact and urgency. Reproduce. Capture environment and recent changes. Assign severity.

## Systematic debugging
Form a hypothesis, find the smallest reproduction, isolate the cause with evidence, fix, then add a regression test. No guessing.

## Tech debt
Log debt with impact and a proposed remediation. Surface recurring debt to the user via the ways-of-working queue.

## Blameless postmortem
Timeline, impact, root cause, what went well, what to improve, action items with owners.

## Maintenance artifact
Triage summary, root cause, fix or follow-up, postmortem actions. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/maintenance.md`.

## References
- https://sre.google/sre-book/postmortem-culture/
