---
name: decision-quality-scoring
category: process
load-when: Post-run analysis, self-assessment, debugging quality issues
skip-when: Normal operation, in-progress work
description: 6-dimension decision quality scoring for Atlas multi-agent workflows. Self-healing doctrine for drift correction.
audience: [atlas-lead, atlas-ent-arch]
tags: [quality, scoring, self-healing, drift, decision-making]
---

# Decision quality scoring

Every Atlas run is scored across 6 dimensions. Scores trend over time, feed into trust profiles, and trigger self-healing when patterns degrade.

## Quick Reference
- 6 dimensions: Role Adherence, Gate Effectiveness, Handoff Quality, Delegation Accuracy, Escalation Quality, Plan Fidelity
- Each scored 0-1, weighted average per run
- Tracked in usage-insights.md, trended over time
- Self-healing: drift alerts auto-created when same failure recurs

## The 6 dimensions

### 1. Role Adherence
Did the role stay within its I DO/DO NOT boundaries?
- Score 1.0: role produced only deliverables it owns
- Score 0.5: role touched files outside its boundary
- Score 0.0: role took over another role's work entirely

Evidence: compare handoff outputs against role definition in agent file.

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
1. Create a drift alert in `lessons.md`
2. Alert is checked during delegation briefing
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
