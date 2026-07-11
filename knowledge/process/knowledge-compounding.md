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
- Retrospective phase runs after deploy in every workflow
- Extracts: new lessons, tool improvements, role corrections, trust updates
- Updates: lessons.md, role playbooks, tool registry, trust profiles
- Cross-run: patterns detected across multiple runs feed into drift alerts
- Human approves all knowledge changes

## Retrospective phase

### When it runs
After deploy phase completes in every workflow (feature, bugfix, etc.)

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

#### 4. Trust updates
Updated trust scores based on run performance:
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
  → Run retrospective phase
  → atlas-lead reviews trajectory.jsonl
  → Extract lessons, tool improvements, role corrections
  → Update trust profiles
  → Present findings to user
  → User approves/rejects each item
  → Approved items update knowledge files
```

## Cross-run learning

### Pattern detection
Across multiple runs, Atlas detects patterns:
```
Pattern: "atlas-qa consistently fails oracle critic on mock patterns"
Runs affected: 3 of last 5
Action: drift alert in lessons.md, role correction in atlas-qa brief
```

### Trend analysis
Trust scores and quality scores trend over time:
```
Trend: atlas-dev quality improving (0.85 → 0.87 → 0.91 over 3 runs)
Trend: atlas-qa rework rate decreasing (0.20 → 0.15 → 0.10 over 3 runs)
```

### Knowledge gaps
When roles consistently struggle with the same type of task:
```
Gap: "No knowledge file for handling concurrent database migrations"
Action: create knowledge/data/concurrent-migrations.md
Approved: pending
```

## Knowledge update protocol

All knowledge updates require human approval:

1. **Atlas proposes** — during retrospective, atlas-lead writes proposed changes
2. **User reviews** — user sees proposed changes with evidence
3. **User approves** — user approves, rejects, or modifies each proposal
4. **Atlas applies** — approved changes update knowledge files
5. **Atlas logs** — changes logged in `knowledge/reference/proposed.md` with approval status

## Storage

### Proposed changes
```
## Proposed (pending approval)
- lesson: "Use dos2unix for CRLF" (source: run-20260711, approved: pending)
- tool-improvement: "Bash validate file exists" (source: run-20260711, approved: pending)
- role-correction: "atlas-qa no mock.verify sole assertion" (source: run-20260711, approved: pending)
```

### Approved changes
```
## Approved
- lesson: "Use dos2unix for CRLF" (source: run-20260711, approved: 2026-07-11)
- tool-improvement: "Bash validate file exists" (source: run-20260711, approved: 2026-07-11)
```

## Anti-patterns

- Extracting lessons without evidence (must cite run + trajectory)
- Skipping retrospective to "save time" (retrospective is mandatory)
- Auto-approving knowledge changes (human must approve)
- Over-extracting (only extract durable, reusable lessons)
- Under-extracting (if something went wrong, it should be captured)
