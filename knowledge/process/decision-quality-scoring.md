---
name: decision-quality-scoring
category: process
status: experimental — opt-in, not part of always-on core
load-when: User explicitly asks for run scoring or drift tracking, or during the monthly self-assessment workflow
skip-when: Normal operation, in-progress work, everyday delegation
description: 6-dimension decision quality scoring for Atlas multi-agent workflows. Self-healing doctrine for drift correction. Scores are the agent's own qualitative judgment with worked anchors, not a measured metric.
audience: [atlas-lead, atlas-ent-arch]
tags: [quality, scoring, self-healing, drift, decision-making, experimental]
---

# Decision quality scoring (experimental)

Every Atlas run can be scored across 6 dimensions. Scores trend over time, feed into trust profiles, and can trigger self-healing when patterns degrade — but the scores are the agent's own honest self-assessment against the anchors below, not a computed metric from measured data. Use this only when the user has asked for it (typically via the monthly `workflows/self-assessment.md` run); don't run it as a mandatory step on ordinary tasks.

## Quick Reference
- 6 dimensions: Role Adherence, Gate Effectiveness, Handoff Quality, Delegation Accuracy, Escalation Quality, Plan Fidelity
- Each scored 0-1, weighted average per run
- Tracked in usage-insights.md, trended over time
- Self-healing: drift alerts auto-created when same failure recurs

## The 6 dimensions

### 1. Role Adherence
Did the role stay within its I DO/DO NOT boundaries? This dimension reuses the always-on `role-adherence` critic's verdict (`knowledge/critic-prompts/role-adherence.md`) rather than re-deriving it — that critic already runs on every deliverable regardless of whether this composite scoring is turned on.
- Score 1.0: role-adherence critic passed clean
- Score 0.5: role-adherence critic found medium-severity findings
- Score 0.0: role-adherence critic found a high-severity finding (took over another role's work entirely)

### 2. Gate Effectiveness
Did gates catch real issues?
- Score 1.0: gate caught a real issue that would have shipped
- Score 0.5: gate found only minor issues
- Score 0.0: gate passed but post-gate analysis found problems

Evidence: gate verdict vs. post-delivery critic findings.

### 3. Handoff Quality
Did the handoff contain everything the next role needed?
- Score 1.0: next role completed without re-reading context
- Score 0.5: next role needed 1-2 additional reads
- Score 0.0: next role could not proceed without significant re-work

Evidence: re-derivation events tracked in trajectory.jsonl.

### 4. Delegation Accuracy
Did atlas-lead route to the correct role?
- Score 1.0: delegated role completed on first attempt
- Score 0.5: completed after re-routing or clarification
- Score 0.0: wrong role delegated, had to re-delegate

Evidence: delegation entries in trajectory.jsonl.

### 5. Escalation Quality
Were escalations well-structured and necessary?
- Score 1.0: escalation included structured payload, was necessary
- Score 0.5: escalation was necessary but poorly structured
- Score 0.0: escalation was unnecessary (could have been resolved at current tier)

Evidence: escalation entries in trajectory.jsonl.

### 6. Plan Fidelity
Did execution follow the plan?
- Score 1.0: execution followed plan with no deviations
- Score 0.5: minor deviations that were resolved
- Score 0.0: major plan change or re-planning required

Evidence: DAG plan vs. actual execution trace.

## Composite scoring

```
composite = (roleAdherence * 0.20) + (gateEffectiveness * 0.15) +
            (handoffQuality * 0.25) + (delegationAccuracy * 0.15) +
            (escalationQuality * 0.10) + (planFidelity * 0.15)
```

Weights are configurable per project. Handoff Quality is weighted highest because it directly impacts downstream roles.

## Role benchmark scoring

The dimensions above score a single run. To compare roles consistently **across** runs, use the fixed suites in `knowledge/benchmark/role-benchmarks.md`:

```
benchmark_score = passing_cases / total_cases   (per category)
```

- Score 1.0: every case in the category passes.
- Score 0.5: about half the cases pass — the role is inconsistent.
- Score 0.0: the category fails wholesale.

The benchmark score is the evidence behind the **Gate Effectiveness** dimension at the category level, and it is the most reliable input to `pass_k_rate` in `role-trust-profiles.md`. Because it is a fixed suite, it is comparable run to run in a way a free-form quality judgment is not.

Like every other score in this file, a benchmark verdict is the agent's own judgment against the benchmark criteria unless the user supplies an external harness. Say so when reporting it. Do not fold the benchmark score into the composite by hand — record it separately and report it beside the composite.

Map each failed benchmark case to a mode in `knowledge/process/failure-mode-taxonomy.md` so repeated failures raise a drift note.

## Storage

Scores are stored in `usage-insights.md` per run:
```
## Quality Scores (run <id>)
- Role Adherence: 0.92
- Gate Effectiveness: 0.88
- Handoff Quality: 0.95
- Delegation Accuracy: 0.90
- Escalation Quality: 1.00
- Plan Fidelity: 0.85
- Composite: 0.91
```

## Self-healing doctrine

When quality scores degrade, Atlas auto-corrects:

### Drift alerts
If a critic fails on the same category in 2+ consecutive runs:
1. Add a drift note to `proposed.md` for the user's batch approval — never write `lessons.md` directly (see `rules/atlas-core.md`)
2. Once approved into `lessons.md`, it's checked during delegation briefing
3. Brief includes: "WARNING: [role] has had [finding] flagged in [N] recent runs"
4. Auto-expires after 30 days of no recurrence

### Role correction injection
If a role consistently fails the same critic:
1. Atlas-lead adds a pre-delegation checklist item for that role
2. Example: if atlas-dev consistently fails oracle critic on mock patterns, brief includes: "Do NOT use mock.verify() -- test observable output only"

### Feedback loop
Drift patterns feed into:
- `lessons.md` (approved lessons)
- `proposed.md` (pending proposals)
- Role playbook updates (via self-assessment cycle)
