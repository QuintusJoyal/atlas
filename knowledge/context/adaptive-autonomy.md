---
name: adaptive-autonomy
category: process
load-when: Kickoff routing, risk classification, autonomy-level selection, mid-task confidence drops
skip-when: Trivial edits with no blast radius, routine single-file changes
description: Risk-tiered autonomy (L0-L3). Continuous risk score routes each task to an autonomy level at runtime; agents escalate one level if confidence drops.
audience: [atlas-lead, all]
tags: [autonomy, risk, hitl, escalation, governance, audit]
---

# Adaptive autonomy

Replaces the binary gate model (auto-approve in small vs explicit sign-off in full) with a continuous, risk-adaptive one. Atlas-lead scores each task at runtime and picks an **autonomy level (L0-L3)** from that score. The level, not the workflow variant, decides how much human involvement a task gets.

This is prompt/schema-based: agents apply the rubric below and record the result. There is no executable classifier.

## Quick Reference
- Score risk 0-100 from four signals, then map to L0-L3.
- Route at runtime from the score — never statically from workflow config or variant alone.
- A task can escalate **one** level mid-task when confidence drops below the threshold.
- Record `autonomyLevel` and `autonomyRationale` in `trajectory.jsonl` for every gated decision.
- Fail safe: when the score is uncertain, round up to the higher level.

## Risk classifier

Score each task by summing four signals. Each signal contributes a weighted number of points; the total is the risk score.

| Signal | 0 points | Partial | Max points | Weight |
| --- | --- | --- | --- | --- |
| File sensitivity | docs, tests, comments | internal app code | auth, secrets, migrations, IaC, CI config, public API contract | 0-40 |
| Blast radius | single file, no dependents | module or one service | shared library, schema, infra, cross-service, data loss possible | 0-30 |
| Security keywords | none | input handling, logging, deps | auth, payment, credential, token, PII, crypto, OWASP terms | 0-20 |
| Prior failure rate | no failures on this path | 1 failure in the last 5 runs | ≥2 failures, or a prior rollback/incident on this path | 0-10 |

`prior failure rate` is read from `$ATLAS_DATA_DIR/runs/*/trajectory.jsonl` (`outcome=failure` / `escalated` entries for the same target or path). Use the run history, not memory.

## Autonomy levels

| Level | Name | When (risk score) | Behavior |
| --- | --- | --- | --- |
| **L0** | Full auto | 0-24 | Agent proceeds and commits without a human gate. Audit entry only. |
| **L1** | Auto with audit trail | 25-49 | Agent proceeds; every decision point recorded in `trajectory.jsonl`. Human reviews the trail after the fact. |
| **L2** | Human review before commit | 50-74 | Agent prepares the change, then pauses for human sign-off before commit/merge/deploy. |
| **L3** | Human-led with agent assist | 75-100 | Human owns the action; agent drafts, explains, and verifies. No autonomous mutation. |

Levels compose with the existing approval gates: L2/L3 make the relevant gate mandatory regardless of variant; L0/L1 may auto-approve a gate that the variant would otherwise enforce.

## Runtime routing (atlas-lead)

At kickoff, and again whenever the task's risk profile changes, atlas-lead:

1. **Scores** the task with the classifier above.
2. **Picks** the level from the table.
3. **Announces** the level and the dominant risk signal to the user.
4. **Records** `autonomyLevel` + `autonomyRationale` in `trajectory.jsonl` (action=`route`).
5. **Applies** the level to every delegation in this task until re-scored.

The selection is dynamic. A workflow's variant (`small`/`full`) and frontmatter set the *baseline* gates, but the risk score overrides them: a `small` feature touching auth routes at L2/L3; a `full` feature touching only docs may route at L0/L1. Variant alone never decides autonomy.

### Re-scoring
Re-score when any of these change: new files enter scope, a security keyword appears, blast radius grows, or a prior failure surfaces. Record the re-score and its rationale.

## Mid-task escalation

A working agent may **escalate exactly one level** (L0→L1→L2→L3) without asking the lead when either:

- its confidence in the current action drops below the threshold (`< 0.7` self-assessed, or any `[USER]`/unknown), or
- the task hits a T1-T4 escalation tier that it cannot resolve at the current level (see `knowledge/context/escalation-tiers.md`).

Escalation is capped at L3 and is one-way for the remainder of the task unless the lead re-scores lower with a recorded rationale. To escalate, the agent:

1. Stops the autonomous action before it mutates anything.
2. Appends a `trajectory.jsonl` entry: action=`escalate`, `autonomyLevel` (new level), `autonomyRationale` (trigger), outcome=`escalated`.
3. Hands the item to the human (L3) or pauses for review (L2).

De-escalation is lead-only and must cite a re-score.

## Audit trail

Every autonomy decision is recorded in the existing trajectory schema (see `knowledge/process/trajectory-logging.md`). Minimum fields:

```jsonl
{
  "ts": "2026-10-17T14:44:00Z",
  "role": "atlas-lead",
  "action": "route",
  "target": "feature/export-endpoint",
  "why": "Touches auth middleware and public API",
  "autonomyLevel": "L2",
  "autonomyRationale": "sensitivity=40, blast=20, security=15 → 75; human review before commit",
  "outcome": "success"
}
```

The rationale must name the signals and the resulting level so a reviewer can reconstruct why autonomy was granted or withheld. If the level is contested later, the entry — not memory — is the record.

## Fail-safe rules

- **Uncertain score → round up.** If signals are ambiguous, choose the higher level.
- **No data is not low risk.** Missing prior-failure history scores 0, but never *lowers* the level below what the other three signals imply.
- **Security keywords are a floor.** A single max-weight security keyword forces at least L2 regardless of the other signals.
- **L3 cannot be auto-downgraded mid-task.** Only a recorded lead re-score can lower it.

## Relationship to other mechanisms

- **Escalation tiers (T1-T4):** stuck-agent protocol. A T1/T2 retry stays at the current autonomy level; T3/T4 forces at least L2/L3 and a human.
- **Approval gates:** gates are the pause points; autonomy levels decide whether the pause is a human or an audit-only checkpoint.
- **Trajectory logging:** the audit substrate. Autonomy fields extend the existing schema, no new store.
- **Role trust profiles:** optional tier allocation for model selection; autonomy level is orthogonal and always applies.
