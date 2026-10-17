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
  "agent_id": "atlas-dev",
  "role": "atlas-dev",
  "phase": "implementation",
  "action": "edit",
  "tool": "edit",
  "target": "src/api.ts:42",
  "duration": 120,
  "tokens_in": 400,
  "tokens_out": 800,
  "tokens": 1200,
  "status": "success",
  "outcome": "success",
  "why": "Fix N+1 query in user endpoint",
  "approach": "Batch query with Promise.all",
  "error": null
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `ts` | yes | ISO 8601 timestamp |
| `agent_id` | yes | Agent identifier (preferably role name). Canonical for trace visualization. |
| `role` | yes | Agent role that made the decision (kept for backward compatibility) |
| `phase` | no | Workflow phase (e.g., requirements, design, implementation, test, review, deploy) |
| `action` | yes | Tool or decision type: edit, read, grep, delegate, escalate, gate-check, plan |
| `tool` | no | Tool name used (alias of `action`; preferred for dashboard visualization) |
| `target` | no | File path, line number, or delegation target |
| `duration` | no | Duration of the action/tool call in milliseconds |
| `tokens_in` | no | Input tokens consumed for this decision/tool call |
| `tokens_out` | no | Output tokens produced for this decision/tool call |
| `tokens` | no | Approximate total tokens consumed by this decision (may equal `tokens_in+tokens_out`) |
| `status` | yes | Canonical outcome: success, failure, blocked, escalated (dashboard uses `status`) |
| `outcome` | yes | Backward-compatible outcome: success, failure, blocked, escalated |
| `why` | yes | Reasoning — why this action was chosen |
| `approach` | no | Specific approach taken (when multiple were possible) |
| `error` | no | Error message/details when `status`/`outcome` is `failure` |
| `delegatedTo` | no | Role delegated to (when action=delegate) |
| `toolInput` | no | Key arguments passed to the tool (for transition analysis) |
| `toolOutput` | no | Summary of tool output: success/failure + key data |
| `errorCategory` | conditional | Error category when outcome/failure (transient/validation/business/permission/not_found) |
| `tokensEstimate` | no | Estimated tokens consumed by tool output |
| `recoveryAction` | conditional | What the agent did after the error (retry/re-escalate/abandon) |
| `toolReceiptId` | conditional | Receipt for file-mutating operations (conflict detection) |
| `checkpointId` | no | Links entry to a checkpoint (when checkpoint system active) |
| `parentId` | no | ID of the entry that caused this one (e.g. a delegation entry that spawned a sub-role's entries) — lets you reconstruct a call tree by grepping for a shared `parentId` without a real tracing backend |

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

## Extended schema example

```jsonl
{
  "ts": "2026-07-11T14:32:00Z",
  "role": "atlas-dev",
  "action": "edit",
  "target": "src/api.ts:42",
  "toolInput": {"file": "src/api.ts", "old": "...", "new": "..."},
  "toolOutput": {"success": true, "linesChanged": 3},
  "tokensEstimate": 400,
  "toolReceiptId": "tr-a7b3c",
  "why": "Fix N+1 query in user endpoint",
  "approach": "Batch query with Promise.all",
  "outcome": "success",
  "tokens": 1200
}
```

## Transition analysis

After a run, compute tool transition frequencies:
```
Tool Transition Matrix (run abc123)
Read -> Read: 4 (re-reading different files)
Read -> Edit: 6 (read-then-edit pattern)
Edit -> Bash: 4 (edit-then-test pattern)
Bash -> Edit: 2 (test-fail-then-fix pattern)
Grep -> Read: 5 (search-then-read pattern)
```

If any transition fires > 80% of the time after a specific tool, it is a candidate for Tool Transition Fusion (composite tool). See `knowledge/process/aci-enforcement.md`.
