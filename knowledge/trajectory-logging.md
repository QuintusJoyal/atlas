---
name: trajectory-logging
category: process
load-when: Debugging failed runs, post-mortem analysis, feeding lessons.md
skip-when: Normal operation, simple tasks
description: JSONL decision trail schema for recording agent reasoning. IDEs implement appending.
audience: [atlas-lead, all]
tags: [trajectory, logging, audit, debugging, jsonl]
---

# Trajectory logging

A lightweight JSONL schema for recording decision points. Purpose: post-hoc analysis, debugging failed runs, learning from patterns, feeding lessons.md.

## Quick Reference
- One JSONL entry per decision point
- Record: who, what, why, outcome
- Append-only, never modify existing entries
- IDEs implement appending via tool hooks or post-action callbacks
- Store at `$ATLAS_DATA_DIR/runs/<run-id>/trajectory.jsonl`

## Schema

Each entry is a single JSON line:

```jsonl
{
  "ts": "2026-07-11T14:30:00Z",
  "role": "atlas-dev",
  "action": "edit",
  "target": "src/api.ts:42",
  "why": "Fix N+1 query in user endpoint",
  "approach": "Batch query with Promise.all",
  "outcome": "success",
  "tokens": 1200
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `ts` | yes | ISO 8601 timestamp |
| `role` | yes | Agent role that made the decision |
| `action` | yes | Tool or decision type: edit, read, grep, delegate, escalate, gate-check, plan |
| `target` | no | File path, line number, or delegation target |
| `why` | yes | Reasoning — why this action was chosen |
| `approach` | no | Specific approach taken (when multiple were possible) |
| `outcome` | yes | success, failure, blocked, escalated |
| `tokens` | no | Approximate tokens consumed by this decision |
| `delegatedTo` | no | Role delegated to (when action=delegate) |
| `error` | no | Error message (when outcome=failure) |

## When to record

Record a trajectory entry when:
- Making a non-obvious decision (multiple valid approaches existed)
- Escalating (T1→T2→T3)
- Delegating to a new role
- Hitting a gate checkpoint
- Encountering an error and recovering
- Completing a phase

Don't record routine reads, greps, or formatting changes. The goal is decision density, not volume.

## Implementation

IDEs implement trajectory logging via:
- Tool call hooks (pre/post action callbacks)
- Post-action append after each significant tool use
- Batch write at phase transitions

The schema is IDE-agnostic. Each IDE implements appending however it wants.

## Usage

### Debugging
Read `trajectory.jsonl` to understand the sequence of decisions that led to a failure. Focus on `why` and `outcome` fields.

### Feeding lessons.md
After a successful run, review trajectory entries where `outcome=failure` followed by `outcome=success`. Extract the pattern as a lesson.

### Metrics
Aggregate `tokens` field per role to understand token consumption patterns. Use for budget optimization.
