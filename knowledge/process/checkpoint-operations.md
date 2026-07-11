---
name: checkpoint-operations
category: process
load-when: Creating, restoring, or forking checkpoints
skip-when: Normal operation
description: Operations for creating, restoring, listing, and forking checkpoints.
audience: [atlas-lead, atlas-ai-eng]
tags: [checkpoint, operations, create, restore, fork, list]
---

# Checkpoint operations

## Create checkpoint

### From atlas-lead
```
Checkpoint created: cp-20260711-001
Level: standard
Phase: implementation
Task: Normalize LF on fetch scripts
Artifacts: atlas/scripts/fetch-docs.sh
Budget: 14,400 tokens used, 35,600 remaining
```

### From any role
When a role completes a task or reaches a natural save point:
```
Checkpoint saved: cp-20260711-002
Level: lightweight
Role: atlas-dev
Current task: Normalize LF on fetch scripts
Owned artifacts: atlas/scripts/fetch-docs.sh
Pending decisions: Whether to use dos2unix or sed
```

### Automatic checkpoint triggers
- Phase transition → standard checkpoint
- Context > 80% window → deep checkpoint
- Before risky operation → standard checkpoint
- End of session → standard checkpoint

## List checkpoints

```
Checkpoints for run-20260711-central-data-home:
  cp-20260711-001 (standard, 2026-07-11T14:30:00Z, phase: implementation)
  cp-20260711-002 (lightweight, 2026-07-11T14:25:00Z, role: atlas-dev)
  cp-20260711-003 (deep, 2026-07-11T12:00:00Z, phase: requirements)
```

## Restore checkpoint

### Resume (fork level 3)
```
Restoring checkpoint: cp-20260711-001
Level: standard
Phase: implementation
Task: Normalize LF on fetch scripts
Artifacts restored: atlas/scripts/fetch-docs.sh
Budget restored: 14,400 tokens used
Ready to continue.
```

### Replay (fork level 1)
```
Replaying from checkpoint: cp-20260711-001
Warning: environment may have changed since checkpoint was created.
Proceeding with replay...
```

### Branch (fork level 2)
```
Branching from checkpoint: cp-20260711-001
Creating new run: run-20260711-alternative-approach
Original task: Normalize LF on fetch scripts
New approach: Try dos2unix instead of sed
```

## Checkpoint validation

Before restoring, validate:
1. Checkpoint file exists and is valid JSON
2. Referenced artifacts still exist (or note which are missing)
3. Budget state is consistent
4. No corruption in trajectory references

```
Validating checkpoint: cp-20260711-001
  ✓ JSON valid
  ✓ Artifacts exist: atlas/scripts/fetch-docs.sh
  ✓ Budget consistent
  ✓ Trajectory references valid
  → Ready to restore
```

## Checkpoint cleanup

Old checkpoints can be cleaned up:
- Keep last 5 checkpoints per run
- Keep all deep checkpoints for active runs
- Auto-delete lightweight checkpoints older than 7 days
- Auto-delete standard checkpoints older than 30 days

```
Cleanup: removed 3 lightweight checkpoints older than 7 days
Cleanup: kept 2 standard checkpoints (active run)
Cleanup: kept 1 deep checkpoint (active run)
```

## Error handling

### Checkpoint not found
```
Error: checkpoint cp-20260711-999 not found
Available checkpoints for this run:
  cp-20260711-001 (standard)
  cp-20260711-002 (lightweight)
```

### Artifact missing
```
Warning: artifact atlas/scripts/fetch-docs.sh not found
The artifact may have been moved or deleted since checkpoint was created.
Options:
  1. Restore without missing artifact
  2. Search for artifact in new location
  3. Abort restore
```

### Context too large
```
Warning: deep checkpoint context is 45,000 tokens
This exceeds the model window. Options:
  1. Restore as standard (drop conversation history)
  2. Compact context and restore
  3. Abort restore
```
