---
name: knowledge-compounding
category: process
load-when: Post-run analysis, retrospective, continuous improvement
skip-when: Normal operation, in-progress work
description: Knowledge compounding system. Post-run extraction, retrospective phase, cross-run learning.
audience: [atlas-lead, atlas-ai-eng]
tags: [knowledge, compounding, learning, retrospective, extraction, continuous-improvement]
---

# Knowledge compounding

Atlas learns from every run. After each workflow completes, a retrospective phase extracts lessons, updates knowledge, and feeds improvements back into the system.

## Quick Reference
- A retrospective phase is native only to `workflows/feature.md` and `workflows/bugfix.md`; other presets don't have one — don't assume it always runs.
- Extracts: new lessons, tool improvements, role corrections. Trust updates are opt-in (see below) — most runs won't have them.
- Updates: `lessons.md` and role playbooks, via the approval flow below — never written directly.
- Cross-run: patterns detected across multiple runs can queue a drift note for `proposed.md`.
- Human approves all knowledge changes.

## Retrospective phase

### When it runs
After the deploy phase, for the workflows that define a retrospective phase (`feature.md`, `bugfix.md`). For other presets, treat this as an optional close-out step, not a mandatory gate — nothing else in this bundle requires it.

### What it extracts

#### 1. Lessons learned
New conventions, anti-patterns, or process improvements:
```
Lesson: "Use dos2unix instead of sed for CRLF normalization on Linux"
Source: run-20260711-central-data-home
Approved: pending
```

#### 2. Tool improvements
Suggestions for tool interface improvements (poka-yoke):
```
Tool improvement: "Bash tool should validate file existence before rm"
Source: run-20260711-central-data-home (error: file not found)
Approved: pending
```

#### 3. Role corrections
Adjustments to role briefs based on performance:
```
Role correction: "atlas-dev brief should always include 'no mock.verify() as sole assertion'"
Source: run-20260711-central-data-home (oracle critic failed)
Approved: pending
```

#### 4. Trust updates (opt-in, experimental)
Only relevant if the user has explicitly opted into `knowledge/process/role-trust-profiles.md` — not part of a default retrospective:
```
Trust update: atlas-dev: 0.85 → 0.87 (quality: 0.92, critic pass: 0.88)
Trust update: atlas-qa: 0.58 → 0.62 (quality: 0.78, critic pass: 0.70)
```

### What it does NOT extract
- Code changes (that's the implementation phase's job)
- Architecture decisions (that's the design phase's job)
- Security findings (that's the security reviewer's job)

## Post-run extraction flow

```
Deploy complete
  → Run retrospective phase (if this workflow has one)
  → atlas-lead reviews trajectory.jsonl
  → Extract lessons, tool improvements, role corrections
  → Update trust profiles (only if opted in)
  → Present findings to user
  → User approves/rejects each item
  → Approved items move to lessons.md; rejected items are dropped
```

## Cross-run learning

### Pattern detection
Across multiple runs, Atlas detects patterns:
```
Pattern: "atlas-qa consistently fails oracle critic on mock patterns"
Runs affected: 3 of last 5
Action: add a drift note to proposed.md for approval, role correction in atlas-qa brief
```

### Trend analysis (opt-in, experimental)
Only meaningful if the user has opted into `decision-quality-scoring.md`/`role-trust-profiles.md` — this bundle doesn't measure either by default:
```
Trend: atlas-dev quality improving (0.85 → 0.87 → 0.91 over 3 runs)
Trend: atlas-qa rework rate decreasing (0.20 → 0.15 → 0.10 over 3 runs)
```

### Knowledge gaps
When roles consistently struggle with the same type of task:
```
Gap: "No knowledge file for handling concurrent database migrations"
Action: create new knowledge file in appropriate subdirectory
Approved: pending
```

## Knowledge update protocol

All knowledge updates require human approval:

1. **Atlas proposes** — during retrospective, atlas-lead appends candidate lessons to `knowledge/reference/proposed.md`
2. **User reviews** — user sees proposed changes with evidence
3. **User approves** — user approves, rejects, or modifies each proposal, in a batch
4. **Atlas applies** — approved items move to `lessons.md`; rejected items are deleted from `proposed.md`. Nothing stays in `proposed.md` marked "approved" — that file is a queue, not an archive.

## Storage

### Proposed changes (queue, in `knowledge/reference/proposed.md`)

Matches that file's actual format:
```
- [ ] Use dos2unix instead of sed for CRLF normalization on Linux. (role: atlas-dev, rationale: sed behaves inconsistently across CRLF edge cases, source: run-20260711-central-data-home, date: 2026-07-11)
```

### Approved changes (moved to `lessons.md`)

Once approved, the item is removed from `proposed.md` and added to `lessons.md` in that file's own format — see `lessons.md` for its structure. `proposed.md` never holds an "approved" section.

## Anti-patterns

- Extracting lessons without evidence (must cite run + trajectory)
- Treating the retrospective as mandatory on presets that don't define one — check the workflow file first
- Auto-approving knowledge changes (human must approve)
- Writing directly to `lessons.md` instead of queuing in `proposed.md`
- Over-extracting (only extract durable, reusable lessons)
- Under-extracting (if something went wrong, it should be captured)
