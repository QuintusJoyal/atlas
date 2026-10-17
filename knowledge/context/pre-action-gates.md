---
name: pre-action-gates
category: process
load-when: Making security, architecture, or delivery decisions
skip-when: Simple edits, formatting, renaming
description: Verification checklists before critical decisions. Don't skip gates for speed.
audience: [all]
tags: [gates, verification, security, architecture, quality]
---

# Pre-action gates

Before critical decisions, verify a short checklist. Don't skip gates for speed.

## Quick Reference
- Security: threat model documented, control addresses specific threat, doesn't break functionality
- Architecture: simpler alternatives considered, trade-offs documented, scale clear
- Final delivery: all criteria met, tests pass, docs complete, rollback exists
- Context freshness: source_mtime within max_staleness_hours, else apply warn/refresh/block policy
- Gate rule: when triggered, pause and verify before proceeding

## Gate checklists

### Security decisions
Before implementing any security control, verify:
1. Threat model is documented
2. Control addresses a specific threat
3. Control doesn't break existing functionality

### Architecture decisions
Before choosing an architecture, verify:
1. Simpler alternatives were considered
2. Trade-offs are documented
3. Scale requirements are clear

### Final delivery
Before marking complete, verify:
1. All acceptance criteria met
2. All tests pass
3. Documentation complete
4. Rollback plan exists

### Context freshness
Before incorporating any loaded knowledge file or handoff artifact, verify:
1. The fragment carries `source_mtime` and `max_staleness_hours` (unknown → treat as `warn`)
2. `now - source_mtime <= max_staleness_hours`, or the phase policy (`warn`/`refresh`/`block`) was applied
3. A `refresh` actually re-read the source; a `block` logged a `stale-context` error

See `knowledge/context/context-freshness.md` for the schema, TTL table, and policies.

## Gate rule
When a pre-action gate triggers, pause and verify the checklist before proceeding. Speed is not a valid reason to skip a gate.
