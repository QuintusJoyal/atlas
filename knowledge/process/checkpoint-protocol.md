---
name: checkpoint-protocol
category: process
load-when: Resuming work, multi-day tasks, context recovery, handoff across surfaces
skip-when: Simple tasks, single-session work
description: Atlas Checkpoint Protocol (ACP) for session persistence. Role-scoped checkpoints, 3-level fork, cross-surface portability.
audience: [atlas-lead, atlas-ai-eng, all]
tags: [checkpoint, session, persistence, fork, recovery, multi-day]
---

# Atlas Checkpoint Protocol (ACP)

ACP enables multi-day work by saving and restoring agent state. Every checkpoint is a complete snapshot of the agent's context, including owned artifacts, delegation state, and pending decisions.

## Quick Reference
- Checkpoint = complete agent state snapshot (not just file list)
- 3 levels of checkpoints: lightweight (in-memory), standard (per-phase), deep (full context)
- 3 levels of fork: replay (re-run), branch (try alternative), resume (continue from checkpoint)
- Cross-surface: checkpoints work across IDEs, terminals, and web UIs
- Stored in `ATLAS_DATA_DIR/checkpoints/`

## Checkpoint structure

```json
{
  "checkpointId": "cp-20260711-001",
  "runId": "run-20260711-central-data-home",
  "level": "standard",
  "created": "2026-07-11T14:30:00Z",
  "role": "atlas-dev",
  "phase": "implementation",
  "variant": "full",
  "context": {
    "currentTask": "Normalize LF on fetch scripts",
    "ownedArtifacts": ["atlas/scripts/fetch-docs.sh"],
    "pendingDecisions": ["Whether to use dos2unix or sed"],
    "delegationState": {
      "delegatedTo": null,
      "delegationBrief": null
    }
  },
  "artifacts": {
    "requirements": "artifacts/requirements.md",
    "design": "artifacts/design.md",
    "code": ["atlas/scripts/fetch-docs.sh"],
    "tests": ["tests/test_fetch_docs.sh"]
  },
  "trajectory": {
    "lastEntry": "tr-20260711-0042",
    "entryCount": 42
  },
  "budget": {
    "predicted": "light",
    "actualTokens": 14400,
    "remaining": 35600
  }
}
```

## 3 levels of checkpoints

### Level 1: Lightweight (in-memory)
- Stored in trajectory.jsonl only
- Minimal state: current task, owned artifacts, pending decisions
- Good for: quick saves within a session
- Restore: fast, minimal context needed

### Level 2: Standard (per-phase)
- Stored as separate JSON file in checkpoints/
- Full phase context: all artifacts, delegation state, budget
- Good for: phase transitions, overnight saves
- Restore: moderate, may need to re-read some files

### Level 3: Deep (full context)
- Stored as JSON + compressed context dump
- Everything in standard + full conversation history + tool outputs
- Good for: multi-day projects, complex debugging sessions
- Restore: full context available, but larger file

## 3 levels of fork

### Fork Level 1: Replay
- Re-run the workflow from this checkpoint
- Same inputs, same decisions
- Good for: reproducing results, testing reproducibility
- Risk: may produce different results if environment changed

### Fork Level 2: Branch
- Create alternative path from this checkpoint
- Different decisions, same context
- Good for: trying alternative approaches, A/B testing
- Risk: context may be stale if files changed

### Fork Level 3: Resume
- Continue from this checkpoint as if no interruption
- Same context, pick up where left off
- Good for: session recovery, context compaction recovery
- Risk: context may need refreshing

## Cross-surface portability

Checkpoints work across surfaces:
- **IDE session** → **terminal session**: checkpoint saved in IDE, restored in terminal
- **Terminal session** → **web UI**: checkpoint saved in terminal, restored in web
- **Any surface** → **any surface**: checkpoints are surface-agnostic JSON

The checkpoint file contains all surface-specific state (tool handles, MCP connections are not portable, but their results are).

## Storage location

```
$ATLAS_DATA_DIR/
  checkpoints/
    cp-20260711-001.json
    cp-20260711-001.context.gz   (level 3 only)
  runs/
    run-20260711-central-data-home/
      ...
```

## When to checkpoint

| Event | Checkpoint level | Reason |
|-------|-----------------|--------|
| Phase transition | Standard | Natural save point |
| Context > 80% window | Deep | Prevents context loss |
| User says "save" | Deep | Explicit request |
| Before risky operation | Standard | Enables rollback |
| End of session | Standard | Enables resume |
| Multi-day project | Deep | Overnight persistence |

## When to fork

| Scenario | Fork level | Reason |
|----------|-----------|--------|
| Want to try alternative | Branch | Low-risk exploration |
| Session crashed | Resume | Continue where left off |
| Need to reproduce result | Replay | Verify reproducibility |
| Context got corrupted | Branch | Start fresh from good state |

## Operations

### Create checkpoint

From atlas-lead:

```text
Checkpoint created: cp-20260711-001
Level: standard
Phase: implementation
Task: Normalize LF on fetch scripts
Artifacts: atlas/scripts/fetch-docs.sh
Budget: 14,400 tokens used, 35,600 remaining
```

From any role, on completing a task or reaching a natural save point:

```text
Checkpoint saved: cp-20260711-002
Level: lightweight
Role: atlas-dev
Current task: Normalize LF on fetch scripts
Owned artifacts: atlas/scripts/fetch-docs.sh
Pending decisions: Whether to use dos2unix or sed
```

### List checkpoints

```text
Checkpoints for run-20260711-central-data-home:
  cp-20260711-001 (standard, 2026-07-11T14:30:00Z, phase: implementation)
  cp-20260711-002 (lightweight, 2026-07-11T14:25:00Z, role: atlas-dev)
  cp-20260711-003 (deep, 2026-07-11T12:00:00Z, phase: requirements)
```

### Restore checkpoint

Resume (fork level 3):

```text
Restoring checkpoint: cp-20260711-001
Level: standard
Phase: implementation
Task: Normalize LF on fetch scripts
Artifacts restored: atlas/scripts/fetch-docs.sh
Budget restored: 14,400 tokens used
Ready to continue.
```

Replay (fork level 1):

```text
Replaying from checkpoint: cp-20260711-001
Warning: environment may have changed since checkpoint was created.
Proceeding with replay...
```

Branch (fork level 2):

```text
Branching from checkpoint: cp-20260711-001
Creating new run: run-20260711-alternative-approach
Original task: Normalize LF on fetch scripts
New approach: Try dos2unix instead of sed
```

### Checkpoint validation

Before restoring, validate:

1. Checkpoint file exists and is valid JSON
2. Referenced artifacts still exist (or note which are missing)
3. Budget state is consistent
4. No corruption in trajectory references

```text
Validating checkpoint: cp-20260711-001
  ✓ JSON valid
  ✓ Artifacts exist: atlas/scripts/fetch-docs.sh
  ✓ Budget consistent
  ✓ Trajectory references valid
  → Ready to restore
```

### Checkpoint cleanup

- Keep last 5 checkpoints per run
- Keep all deep checkpoints for active runs
- Auto-delete lightweight checkpoints older than 7 days
- Auto-delete standard checkpoints older than 30 days

```text
Cleanup: removed 3 lightweight checkpoints older than 7 days
Cleanup: kept 2 standard checkpoints (active run)
Cleanup: kept 1 deep checkpoint (active run)
```

### Error handling

Checkpoint not found:

```text
Error: checkpoint cp-20260711-999 not found
Available checkpoints for this run:
  cp-20260711-001 (standard)
  cp-20260711-002 (lightweight)
```

Artifact missing:

```text
Warning: artifact atlas/scripts/fetch-docs.sh not found
The artifact may have been moved or deleted since checkpoint was created.
Options:
  1. Restore without missing artifact
  2. Search for artifact in new location
  3. Abort restore
```

Context too large:

```text
Warning: deep checkpoint context is 45,000 tokens
This exceeds the model window. Options:
  1. Restore as standard (drop conversation history)
  2. Compact context and restore
  3. Abort restore
```
