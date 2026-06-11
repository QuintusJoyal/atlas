---
name: atlas-docs-playbook
description: Documentation methodology for atlas-docs: Diataxis types and templates. Use when atlas-docs runs.
disable-model-invocation: true
---

# Technical writer playbook

Standards: the Diataxis framework. Always apply `writing-style.mdc` (no em dashes, no AI tells).

## Diataxis: pick the type
- Tutorial: learning-oriented, step by step.
- How-to guide: task-oriented, goal first.
- Reference: information-oriented, accurate and complete.
- Explanation: understanding-oriented, the why.

## Templates
- README: what it is, why, install, usage, configuration, links.
- Changelog: keep-a-changelog style grouped by Added, Changed, Fixed, Removed under a version.
- Runbook: symptom, diagnosis, steps to resolve, escalation.

## Quality
Accurate, concise, audience-appropriate. Show, do not tell. Verify commands and code samples.

## Docs artifact
The right document type for the audience. Persist to `.atlas/runs/<run-id>/docs.md` or the target file. Publishing via MCP needs user approval.

## References
- https://diataxis.fr/
