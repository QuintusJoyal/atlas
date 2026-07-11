---
name: self-assessment-protocol
category: process
load-when: Monthly self-assessment, reviewing Atlas capabilities, planning improvements
skip-when: Normal operation
description: Protocol for monthly self-assessment of Atlas. Gated self-modification loop with human approval.
audience: [atlas-lead, atlas-ent-arch, atlas-ai-eng]
tags: [self-assessment, improvement, monthly, gated, self-modification]
---

# Self-assessment protocol

Atlas runs a monthly self-assessment to evaluate its own performance and identify improvements. All changes require human approval.

## Quick Reference
- Monthly trigger (user-initiated)
- 4 phases: Benchmark Review, Performance Analysis, Gap Identification, Improvement Proposals
- 3 risk tiers for self-modification (T1: auto, T2: gate, T3: human required)
- Human always has final approval
- Runs as a workflow (workflows/self-assessment.md)

## 4 phases

### 1. Benchmark Review
- Review `knowledge/benchmark/frontier-benchmark.md`
- Compare against current frontier harnesses
- Identify new gaps or improvements
- Update benchmark if frontier harnesses have released new features

### 2. Performance Analysis
- Review quality scores from `knowledge/process/decision-quality-scoring.md`
- Analyze trust profile trends from `knowledge/process/role-trust-profiles.md`
- Review drift alerts from `knowledge/reference/lessons.md`
- Identify patterns across recent runs

### 3. Gap Identification
- Compare benchmark gaps against performance analysis
- Prioritize gaps by impact and effort
- Classify each gap: must-fix, should-fix, nice-to-have

### 4. Improvement Proposals
- For each prioritized gap, create an improvement proposal
- Each proposal includes: what, why, risk tier, estimated impact
- Present proposals to user for approval

## 3 risk tiers for self-modification

### T1: Auto-approve (low risk)
Changes that don't affect agent behavior:
- Adding new knowledge files
- Updating documentation
- Adding new examples
- Formatting changes

Action: Atlas can auto-approve, log in `knowledge/reference/proposed.md`

### T2: Gate required (medium risk)
Changes that affect agent behavior but are reversible:
- Updating role briefs
- Adding new critics
- Modifying workflow phases
- Changing trust score weights

Action: Requires user approval via gate check

### T3: Human required (high risk)
Changes that affect core rules or are hard to reverse:
- Modifying atlas-core.md non-negotiables
- Changing delegation rules
- Adding new roles
- Modifying the critic system

Action: Requires explicit human approval, cannot be auto-approved

## Self-modification loop

```
Monthly trigger
  → Run self-assessment workflow
  → Phase 1: Benchmark Review
  → Phase 2: Performance Analysis
  → Phase 3: Gap Identification
  → Phase 4: Improvement Proposals
  → Present to user
  → User approves/rejects each proposal
  → Apply approved changes
  → Log changes in CHANGELOG.md
  → Update frontier-benchmark.md
```

## Gated self-modification rules

1. **Human always approves** — no change is applied without user approval
2. **Risk tier determines gate** — T1 auto, T2 gate, T3 human required
3. **Changes are reversible** — prefer additive changes over modifications
4. **Changes are logged** — every change recorded in CHANGELOG.md and `knowledge/reference/proposed.md`
5. **Changes are tested** — new knowledge/critics should be validated on a sample task before full deployment

## Anti-patterns

- Skipping self-assessment because "things are working fine"
- Auto-approving T2/T3 changes without user review
- Making changes without evidence from performance analysis
- Not logging changes in CHANGELOG.md
- Making irreversible changes (prefer additive)
