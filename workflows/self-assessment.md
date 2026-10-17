---
name: self-assessment
description: Monthly self-assessment workflow. Reviews Atlas performance, identifies gaps, proposes improvements.
type: pipeline
triggers:
  - monthly-review
  - self-assessment
  - capability-review
variants:
  small:
    description: Quick self-assessment. Benchmark review + performance analysis only. No gate — this variant never reaches the improvement-proposals phase where the final gate lives.
    gates: []
    skip: [gap-analysis, improvement-proposals]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Full self-assessment. All 4 phases with improvement proposals.
    gates: [final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions: []
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: self-assessment

Monthly self-assessment workflow. Reviews Atlas performance against frontier harnesses and proposes improvements.

## Variant selection

- **small:** quick check, no improvement proposals. Good for monthly status update.
- **full:** complete assessment with improvement proposals. Good for quarterly review.

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### benchmark-review
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-ent-arch (premium)
- **Input:** knowledge/benchmark/frontier-benchmark.md, current frontier harness features
- **Output:** updated benchmark with new findings
- **See:** `knowledge/benchmark/frontier-benchmark.md`

### performance-analysis
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-ai-eng (standard)
- **Input:** knowledge/reference/lessons.md always; knowledge/process/decision-quality-scoring.md and knowledge/process/role-trust-profiles.md only if the user has opted into those experimental mechanisms — otherwise this phase works from knowledge/reference/lessons.md and trajectory logs alone
- **Output:** performance summary with trends and patterns
- **See:** `knowledge/process/decision-quality-scoring.md`

### gap-analysis
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-ent-arch (premium), atlas-consultant (standard)
- **Input:** benchmark findings, performance summary
- **Output:** prioritized gap list with impact/effort ratings
- **Skip-if:** variant=small

### improvement-proposals
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-ent-arch (premium)
- **Input:** prioritized gaps, current Atlas capabilities
- **Output:** improvement proposals with risk tiers
- **Human approval:** required for all T2/T3 changes
- **Skip-if:** variant=small
- **See:** `knowledge/process/self-assessment-protocol.md`

## Definition of Done

- [ ] Benchmark updated with current frontier harness features
- [ ] Performance trends analyzed (knowledge/reference/lessons.md and trajectory patterns always; quality scores/trust profiles/drift alerts only if those experimental mechanisms are opted in)
- [ ] Gaps prioritized by impact and effort (full only)
- [ ] Improvement proposals created with risk tiers (full only)
- [ ] User has approved/rejected all proposals (full only)
- [ ] Approved changes applied and logged in CHANGELOG.md (full only)

## Lite mode

Generated into `lite/workflows/self-assessment.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# Workflow: self-assessment (Lite)

Quick monthly review of Atlas performance.

## Phases

### review
- **Roles:** atlas-lead
- **Input:** recent runs, quality scores
- **Output:** summary of what worked, what didn't, 1-3 improvement ideas

### propose
- **Roles:** atlas-lead
- **Input:** review summary
- **Output:** list of proposed changes for user approval
<!-- lite:end -->
