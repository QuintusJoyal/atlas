---
name: agent-behavior-anomaly-detection
category: security
status: opt-in procedure — analysis over existing run artifacts, no runtime monitor ships in this bundle
load-when: User asks what an agent did, requests behavior monitoring or anomaly scoring, or a run needs a security investigation or forensic review
skip-when: Normal development work, routine delegation, tasks with no security question on the table
description: Security-focused anomaly detection for agent behavior — per-role behavior baselines, anomaly scoring with configurable sensitivity thresholds, escalation into incident response and human-in-the-loop approval, and forensic replay for post-incident investigation.
audience: [atlas-security, atlas-lead, atlas-devops]
tags: [anomaly, detection, behavior, baseline, scoring, forensics, escalation, monitoring, security]
---

# Agent behavior anomaly detection

Detects risky prompts, unauthorized decisions, abnormal activity patterns, and boundary violations in what agents do during a run. It is the security counterpart to `knowledge/process/observability-system.md` (which tracks health and failure patterns): this file tracks hostile or out-of-bounds behavior.

## Scope and honesty

- Nothing here runs automatically. This bundle ships no telemetry pipeline, no live alerting, no anomaly daemon. What follows is an analysis an agent performs when asked, over data that already exists: trajectory logs (`knowledge/process/trajectory-logging.md`), gate and handoff artifacts under `$ATLAS_DATA_DIR/runs/`, and the phase tool scope in `knowledge/process/role-tool-scoping.md`.
- Scores are judgments against stated anchors and a stated baseline, not measured probabilities. Every score you report names the rule or deviation that produced it and the sample size behind it. Below warm-up, say "no baseline yet" instead of scoring.
- Trajectory logs record decisions, not raw prompts. Never copy full prompt text, secrets, or PII into logs, scores, or reports (see Redaction and retention).

## Quick Reference

- Baseline per role: 6 dimensions, warm-up 20 decisions across 3 runs, rolling update
- Score: 0.00-1.00 = statistical deviation (60%) + rule hits (40%), any Critical rule floors it at 0.90
- Sensitivity: strict / standard / lenient sets the review, escalate, and stop thresholds
- Bands map to escalation tiers: review = note, escalate = T3 to user, stop = T4 + human re-approval
- Evidence: trajectory `ts` + `parentId` call trees, preserved append-only for forensics
- Store: `$ATLAS_DATA_DIR/behavior-baselines.json`, `$ATLAS_DATA_DIR/anomaly-config.json`

## Behavior baseline per role

Each role gets its own baseline. Roles differ by design (atlas-dev writes constantly, atlas-reviewer never does), so a shared baseline would flag normal work as anomalous.

| Dimension | Source field(s) | What it catches |
|-----------|-----------------|-----------------|
| Action mix | `action` share per role | A reviewer starting to edit, a role suddenly running shell |
| Decision rate | entries per run | Bursts of activity that no task justifies |
| Escalation rate | `action=escalate` share | Escalation storms, or a role that never escalates |
| Failure rate | `outcome=failure` share | Repeated failure loops with changed targets |
| Cost per decision | `tokens` average | Token burn far above the role's usual spend |
| Scope spread | distinct `target` roots | One task touching many unrelated directories |

Rules:

1. **Warm-up:** no scoring until 20 decisions across at least 3 runs. Report "no baseline yet" and observe only.
2. **Update:** after each run the user has reviewed, fold the run in with exponential moving average (alpha 0.2). Never update a baseline from a run that is still under investigation.
3. **Decay:** baselines older than 30 days are stale; re-enter warm-up for scoring rather than comparing against old habits.
4. **Storage:** `$ATLAS_DATA_DIR/behavior-baselines.json`, one block per role (`taskCount`, per-dimension mean/median and spread, `lastUsed`, `warmupRemaining`).

## Detection rules

| ID | Signal | Source | Severity |
|----|--------|--------|----------|
| RB-1 | Risky prompt patterns: instruction override ("ignore previous instructions"), gate/safety disable requests, credential harvesting, exfiltration of repo content to external endpoints | task brief, `why`, `toolInput` | Critical |
| UD-1 | Tool use outside the phase's permitted set in `knowledge/process/role-tool-scoping.md` | `action` vs phase scope | High |
| UD-2 | Phase transition without a `gate-check` entry, or a gate marked pass with no critic verdict | gate artifacts vs trajectory | Critical |
| UD-3 | Delegation outside the target role's I DO list, or atlas-lead delegating to itself | `action=delegate`, `delegatedTo` | High |
| AA-1 | Decision count or token burn > 2.5 sigma above role baseline and >= 2x absolute | baseline vs run totals | Medium |
| AA-2 | Same failure mode repeated across distinct targets (the Repeater/Looper patterns from `knowledge/process/observability-system.md`) | `outcome=failure`, `error` | Medium |
| DB-1 | Reads or touches under secret paths, PII stores, or paths outside the task scope named in the brief | `target`, `toolInput` | Critical if secrets/PII, else High |
| DB-2 | Writes to files the task brief and handoff do not imply | `action=edit/bash` vs declared scope | High |

## Anomaly scoring

1. **Collect the window** — trajectory entries for the role and time range under review, plus the gate/handoff artifacts for the same run.
2. **Score deviation** — for each baseline dimension, compute how far the observed value sits from the baseline median, scaled by the baseline spread. Use median absolute deviation (robust for small samples). Cap each dimension's contribution at 1.0. Dimensions with no baseline contribute 0 and are listed as "not scored".
3. **Score rules** — each triggered rule contributes its severity weight: Medium 0.25, High 0.50, Critical 0.75.
4. **Combine** — `score = clamp(0.60 * deviation + 0.40 * ruleScore, 0, 1)`. Any triggered Critical rule floors the score at 0.90 regardless of the formula.
5. **Apply thresholds** — sensitivity setting decides the band:

| Sensitivity | Review (note in run) | Escalate (T3, human) | Stop (T4, halt role) |
|-------------|----------------------|----------------------|----------------------|
| strict | 0.25 | 0.45 | 0.70 |
| standard (default) | 0.40 | 0.65 | 0.85 |
| lenient | 0.55 | 0.80 | 0.95 |

Sensitivity lives in `$ATLAS_DATA_DIR/anomaly-config.json` and is set by the user. An agent may propose a threshold change with evidence, never apply one silently.

## Escalation to human-in-the-loop

Bands map to the tiers in `knowledge/context/escalation-tiers.md`:

| Band | Tier | Action |
|------|------|--------|
| Below review | none | Log nothing beyond the trajectory entry itself |
| Review | — | Note the finding in the run's handoff; mention it at the next gate |
| Escalate | T3 | Pause the role, present score, triggered rules, evidence lines, and a recommendation to the user (option A / option B / recommendation) |
| Stop | T4 | Halt the role and its pending delegations immediately, notify the user now, no options presentation |

The human is the approval authority, not a reviewer of last resort:

- A stop-band finding means the role does not resume until the user signs off, the same way approval gates work in `rules/atlas-core.md`. No agent may waive, auto-approve, or downgrade its own finding.
- Escalation payload minimum: score, sensitivity setting, triggered rule IDs, evidence references (`ts` plus `target` on each trajectory line), baseline sample size, and the recommended action.
- Sensitivity changes, threshold waivers, and baseline resets are user decisions.

## Integration with incident response

A confirmed stop-band finding is a security incident. Follow `knowledge/delivery/incident-response.md` with these agent-specific adjustments:

1. **Triage** — severity follows the finding: RB-1, UD-2, or DB-1 with secrets/PII is SEV1-equivalent (stop the affected work); High without data exposure is SEV2-equivalent.
2. **Containment** — pause the role, cancel its pending delegations, and narrow its tool scope (`knowledge/process/role-tool-scoping.md`). Do not attempt containment of a live breach unless the user authorizes it (`rules/security.md`).
3. **Evidence preservation** — trajectory logs and run artifacts are append-only. Never edit, truncate, or delete them during response; note the run id and role in the incident record instead.
4. **Eradication** — identify what the role was responding to: an injected instruction in retrieved content, an over-broad tool grant, a poisoned knowledge file. Rotate any credential that appeared in the window.
5. **Recovery** — resume only after user sign-off, with the tool scope that caused the finding removed or justified.
6. **Postmortem** — blameless write-up plus a proposed lesson in `knowledge/reference/proposed.md` (`knowledge/process/knowledge-compounding.md`).

## Forensic analysis

Post-incident replay over frozen run artifacts:

1. **Freeze** — copy the run directory path into the incident record; make no changes to it.
2. **Window** — filter trajectory entries by `ts` around the finding.
3. **Reconstruct** — grep the shared `parentId` to rebuild the call tree from the triggering delegation down (`knowledge/process/trajectory-logging.md`).
4. **Drill down** — per-role table: observed dimension values against baseline, with deltas.
5. **Evidence list** — one row per triggered rule: rule ID, log line (`ts` + `target`), and the field that matched. No rule may appear in the report without a line reference.
6. **Human timeline** — gate approvals and escalations interleaved with machine actions, so the report shows exactly where a human did and did not look.
7. **Verdict** — confirmed incident, false positive, or unresolved, with what would have made detection earlier.

Reports live beside the run under `$ATLAS_DATA_DIR/runs/<run-id>/` and follow the same redaction rules as the logs.

## Tuning and false positives

- Record every verdict (confirmed / false positive / unresolved) so threshold changes are argued from evidence, not from annoyance.
- New roles and new projects start in warm-up. Widen a baseline before raising a threshold; raising thresholds hides real incidents along with the noise.
- Never tune a threshold to silence a finding you cannot explain. Unexplained means unresolved, not benign.
- Review the rule set after each incident: a rule that never fires on real incidents is a candidate for removal; a class of incidents no rule caught is a candidate for a new rule.

## Redaction and retention

- Store references, not content: file path, line number, action, and outcome. Where content matters (a risky prompt pattern), store the matched pattern and a redacted excerpt, never the whole input.
- Strip tokens, keys, connection strings, and PII patterns before anything is written to a score, report, or baseline.
- Scores, baselines, and reports inherit the retention of the run artifacts they came from; deleting a run deletes its derived analysis.
- Baselines are aggregates over decisions, not a record of what any person typed. Do not put user-identifying data in them.
