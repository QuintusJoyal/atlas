---
name: failure-mode-taxonomy
category: process
load-when: Reviewing failed runs, drift alerts, self-assessment, mapping benchmark failures
skip-when: Normal operation, healthy runs
description: Structured taxonomy of known Atlas failure modes for consistent labeling, pattern detection across runs, and connection to the drift alert system.
audience: [atlas-lead, atlas-ai-eng, atlas-ent-arch]
tags: [failure-modes, taxonomy, drift, postmortem, quality, self-assessment]
---

# Failure mode taxonomy

A fixed vocabulary for naming what went wrong. Label failures with a mode ID so patterns are detectable across runs instead of re-described each time. Feeds drift alerts in `knowledge/process/decision-quality-scoring.md`, role correction in `knowledge/process/role-trust-profiles.md`, and benchmark failure signals in `knowledge/benchmark/role-benchmarks.md`.

## Quick Reference
- 15 modes across 6 categories
- Label every failed critic, gate, or benchmark case with one mode ID
- Same mode in 2+ consecutive runs → drift note in `proposed.md`
- Same mode in 3+ consecutive runs on the same role → pre-delegation checklist item

## Categories

| Prefix | Category | What it covers |
|--------|----------|----------------|
| ORCH | Orchestration | Lead behavior, routing, delegation |
| ROLE | Role boundary | Scope creep, overstepping, drift |
| REQ | Requirements | Scope, ambiguity, acceptance criteria |
| REASON | Reasoning | Convergence, grounding, planning |
| VERIFY | Verification | False passes, skipped proof, gate theater |
| PROCESS | Process | Context, handoff, recovery, compliance |

## Modes

### ORCH — Orchestration

| ID | Mode | Symptom | Detected by | Mitigation |
|----|------|---------|-------------|------------|
| ORCH-01 | Lead collapses into implementation | Lead writes code or specialist artifacts inline | role-adherence critic; trajectory `action=edit` by atlas-lead | Re-delegate; tighten `rules/atlas-lead-orchestration.md` |
| ORCH-02 | Under-scoped brief | Specialist guesses where its job ends; scope creep follows | role-adherence critic | Restate the receiving role's I DO NOT list in the brief |
| ORCH-03 | Delegation naming violation | `description` lacks `atlas-<role>:` or mismatches `role` | delegation payload check | Reject and resend the delegation |
| ORCH-04 | Wrong-role routing | Work delegated to a role that does not own it | delegation accuracy score; re-routing event | Re-delegate to the owner per `ROLES.md` |

### ROLE — Role boundary

| ID | Mode | Symptom | Detected by | Mitigation |
|----|------|---------|-------------|------------|
| ROLE-01 | Role oversteps boundary | A role produces another role's deliverable | role-adherence critic (high severity) | Re-delegate to the owner; boundary note in brief |
| ROLE-02 | Role drift | Deliverable slowly departs from the brief over a run | trajectory plan-fidelity check | Mid-run re-brief; checkpoint comparison |
| ROLE-03 | Scope creep by helpfulness | Role adds unrequested work because it "seemed useful" | spec-integrity critic; diff review | Tighten out-of-scope list in the brief |

### REQ — Requirements

| ID | Mode | Symptom | Detected by | Mitigation |
|----|------|---------|-------------|------------|
| REQ-01 | Unclear acceptance criteria | Stories exist but nothing is testable | requirements gate; atlas-qa | Re-delegate requirements to atlas-pm |
| REQ-02 | Scope creep | Work exceeds the agreed requirements | scope-change detection; spec-integrity critic | Pause, re-evaluate, present options |

### REASON — Reasoning

| ID | Mode | Symptom | Detected by | Mitigation |
|----|------|---------|-------------|------------|
| REASON-01 | Premature convergence | First plausible option chosen, alternatives ignored | socratic-quality critic; trade-off analysis | Require an ADR with rejected options |
| REASON-02 | Ungrounded claim | Fabricated API, file, or citation | oracle critic; observe-before-act check | Require read-before-assert evidence |
| REASON-03 | Plan drift | Execution diverges from the DAG plan | plan-fidelity score | Pause and re-plan; update budget.md |

### VERIFY — Verification

| ID | Mode | Symptom | Detected by | Mitigation |
|----|------|---------|-------------|------------|
| VERIFY-01 | False pass | Gate or critic passes work that later fails | post-gate critic findings; pass^k disagreement | Raise k for that gate; add benchmark case |
| VERIFY-02 | Skipped self-verification | Deliverable shipped with no test, lint, or check | trace-based scoring (self-verification rate) | Block on evidence of verification |
| VERIFY-03 | Gate theater | Gate marked passed without a real evaluation | gate-check trajectory entry missing | Re-run the gate in a separate context |

### PROCESS — Process

| ID | Mode | Symptom | Detected by | Mitigation |
|----|------|---------|-------------|------------|
| PROCESS-01 | Context loss | Next role re-reads what the handoff should carry | re-derivation events in trajectory.jsonl | Enrich the handoff contract |
| PROCESS-02 | Rework loop | Same task re-delegated repeatedly without converging | rework rate; repeated failure entries | Root-cause with 5-whys; escalate |
| PROCESS-03 | Compliance gap unflagged | Regulated work proceeds without a compliance check | compliance gate; atlas-compliance | Inject the compliance phase at kickoff |

## Pattern detection

1. On every failure, attach one mode ID to the trajectory entry (`errorCategory` plus the mode in `why`).
2. Aggregate mode counts per run in `usage-insights.md`.
3. Same mode in 2+ consecutive runs → add a drift note to `proposed.md` for batch approval (never write `lessons.md` directly — see `rules/atlas-core.md`).
4. Same mode in 3+ consecutive runs on one role → add a pre-delegation checklist item for that role.
5. Once approved into `lessons.md`, the mode is surfaced during delegation briefing and auto-expires after 30 days without recurrence.

## Anti-patterns

- Inventing a new mode name for a known failure instead of reusing an ID.
- Labeling only the symptom ("tests failed") without the underlying mode.
- Filing a drift note directly in `lessons.md`.
