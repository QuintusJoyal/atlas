---
name: dag-orchestration
category: process
load-when: Planning multi-role execution, optimizing parallelism, large-feature decomposition
skip-when: Simple tasks, single-role work
description: DAG-based task orchestration for Atlas. Dynamic construction, critical path analysis, parallel safety, critic nodes.
audience: [atlas-lead, atlas-ent-arch]
tags: [dag, orchestration, parallel, critical-path, decomposition]
---

# DAG orchestration

Atlas-lead constructs a Directed Acyclic Graph (DAG) for each workflow. The DAG defines task dependencies, enables parallel execution, and identifies the critical path.

## Quick Reference
- DAG = directed acyclic graph of tasks with dependencies
- Dynamic construction from workflow phases + conditions
- Critical path analysis identifies bottleneck tasks
- Parallel safety: concurrent tasks don't touch overlapping artifacts
- Critic nodes: gate checks are DAG nodes with fan-in from multiple roles
- Visual: ASCII DAG in budget.md for user visibility

## DAG construction

### From workflow definition
Each workflow defines phases with roles and parallel flags. Atlas-lead converts this to a DAG:

```
Workflow: feature (full)
Phases: requirements → design → implementation → test → review → deploy

DAG:
  requirements[pm] → design[architect,ux] → implementation[dev] → test[qa] → review[ent-arch] → deploy[devops]
                    ↗                       ↗
                   parallel               parallel
```

### Dynamic conditions
Conditions inject additional nodes:
```
IF has-database:  design → database-design[dba] → implementation
IF has-security:  design → security-review[security] → implementation
IF has-api:       design → api-design[be] → implementation
```

### Parallel safety check
Before marking tasks as parallel, verify they don't touch overlapping artifacts:
```
parallel-safe(atlas-architect, atlas-ux):
  architect touches: docs/architecture.md, docs/data-model.md
  ux touches: docs/ux-spec.md
  overlap: none → parallel-safe ✓

parallel-safe(atlas-dev, atlas-qa):
  dev touches: src/app.py, src/utils.py
  qa touches: tests/test_app.py, tests/test_utils.py
  overlap: none → parallel-safe ✓
```

If overlap detected, make tasks sequential.

## Critical path analysis

The critical path is the longest sequence of dependent tasks. Any delay on the critical path delays the entire workflow.

```
Critical path: requirements(200) → design(350) → implementation(1400) → test(800) → review(400) = 3150 tokens
Parallel path: ux-spec(300) → [joins implementation]
Database path: database-design(250) → [joins implementation]

Critical path determines minimum workflow duration.
```

### Critical path implications
- Tasks on critical path get priority for model tier allocation
- Parallel paths can use lower tiers without affecting overall timeline
- If critical path task fails, entire workflow pauses
- Budget predictions are based on critical path, not all tasks

## Parallel execution safety

### Artifact conflict detection
Before parallel execution, check for artifact conflicts:
```
Task A touches: src/app.py, src/config.py
Task B touches: src/app.py, src/utils.py
Conflict: src/app.py
Resolution: make sequential (A → B)
```

### Read-only sharing
Multiple tasks can read the same file:
```
Task A reads: docs/architecture.md
Task B reads: docs/architecture.md
Safe: both read-only → parallel OK
```

### Write exclusion
If any task writes a file, no other task can read or write it concurrently:
```
Task A writes: src/app.py
Task B reads: src/app.py
Unsafe: write + read → make sequential
```

## Visual DAG (budget.md)

Atlas-lead generates an ASCII DAG in budget.md for user visibility:

```
## Execution DAG

  ┌─────────────┐
  │ requirements │
  │   (atlas-pm) │
  └──────┬──────┘
         │
  ┌──────┴──────┐
  │    design    │
  │ ┌────┴────┐ │
  │ │architect│ │
  │ │   ux    │ │
  │ └────┬────┘ │
  └──────┼──────┘
         │
  ┌──────┴──────┐
  │implementatn  │
  │  (atlas-dev) │
  └──────┬──────┘
         │
  ┌──────┴──────┐
  │    test     │
  │  (atlas-qa) │
  └──────┬──────┘
         │
  ┌──────┴──────┐
  │   review    │
  │(atlas-ent-a)│
  └──────┬──────┘
         │
  ┌──────┴──────┐
  │   deploy    │
  │(atlas-devops)│
  └─────────────┘

Critical path: requirements → design → implementation → test → review → deploy
Estimated total: 3,150 tokens
Parallel benefit: ux-spec runs parallel with architect (saves 300 tokens)
```

## Integration with existing systems

### With workflow state machine
DAG nodes map to workflow phases. Phase state transitions are triggered when all DAG dependencies for that phase complete.

### With checkpoint protocol
Phase transitions trigger a standard checkpoint (see `knowledge/process/checkpoint-protocol.md`), independent of DAG bookkeeping.

### With critic system
Gate checks wait for all contributing tasks in a phase to complete before evaluating.

### With budget prediction
Budget predictions should track the critical path, not the sum of all tasks (parallel tasks don't add to timeline) — but keep estimates as rough ranges, not fabricated precision.
