---
name: adversarial-critics
category: process
load-when: Running gate checks, designing critic loops, evaluating deliverables
skip-when: Normal delegation, simple tasks
description: 6 built-in adversarial critics for Atlas. Role-adherence (default, lightweight), spec-integrity (gapped), oracle (gapped), implementation, Socratic-quality, regression-gate.
audience: [atlas-lead, atlas-ent-arch]
tags: [critics, adversarial, evaluation, quality, multi-perspective]
---

# Adversarial critics

Atlas uses 6 built-in critics that evaluate deliverables from different perspectives. Critics are adversarial: they actively look for failures, not confirm what works.

## Quick Reference
- 6 critics: role-adherence (default, immediate), spec-integrity (gapped), oracle (gapped), implementation, socratic-quality, regression-gate
- **role-adherence is the default lightweight critic** referenced in `rules/atlas-core.md` — runs on every deliverable, needs no history or infrastructure. See `knowledge/critic-prompts/role-adherence.md`.
- 3 "gapped" critics: spec-integrity, oracle, regression-gate
- Gapped critics = 2 runs delayed (they review the NEXT run, not the current one)
- 3 normal critics: role-adherence, implementation, socratic-quality (run immediately after delivery)
- 3-pass/3-fail: 3 consecutive passes = auto-approve (no critic for next run), 3 consecutive failures = mandatory re-work — this auto-tuning applies to the 5 fuller critics (opt-in); role-adherence always runs since it's cheap
- All critics return structured JSON: {critic, target, verdict, findings, evidence, confidence}

## The 6 critics

### 0. role-adherence (immediate, default)
**Purpose:** Verify the producing role stayed inside its own I DO / I DO NOT boundaries.
**Runs:** Immediately after every deliverable, from any role. This is the one critic that isn't opt-in — see `rules/atlas-core.md`.
**How:** Compares the deliverable's files/actions against the role's own agent file boundaries. No trust scores, no composite metrics, no history needed.
**Return:** {critic, target, verdict: pass/fail, findings: [{category, severity, detail}], evidence: "file or action reference", confidence: 0-1}
**Full prompt:** `knowledge/critic-prompts/role-adherence.md`

### 1. spec-integrity (gapped)
**Purpose:** Verify what was built matches what was specified.
**Runs:** 2 runs delayed (next run's implementation phase).
**How:** Takes the original requirements artifact and the actual diff, checks coverage. Reports untested scenarios, unclear acceptance criteria, and scope gaps.
**Return:** {critic, target, verdict: pass/fail, findings: [{category, severity, detail}], evidence: "diff-range", confidence: 0-1}

**Why gapped:** The diff is more meaningful after adjacent changes land. Looking at a diff in isolation misses integration issues.

### 2. oracle (gapped)
**Purpose:** Detects oracle leakage — tests that pass but verify the wrong behavior.
**Runs:** 2 runs delayed (next run's implementation phase).
**How:** For each test assertion, checks whether the assertion actually constrains the behavior or just validates a tautology. Flags: mock.verify() as only assertion, assertion count == 1 for complex changes, all assertions test same path.
**Return:** {critic, target, verdict: pass/fail, findings: [{category, severity, detail}], evidence: "test-file:line", confidence: 0-1}

**Why gapped:** Test quality is best judged after the tests have had a chance to run in CI and catch real regressions.

### 3. implementation (immediate)
**Purpose:** Verify the implementation is sound — correct patterns, no regressions, follows standards.
**Runs:** Immediately after implementation phase.
**How:** Reviews code changes for correctness, adherence to coding standards, proper error handling, and no introduction of known anti-patterns.
**Return:** {critic, target, verdict: pass/fail, findings: [{category, severity, detail}], evidence: "file:line", confidence: 0-1}

### 4. socratic-quality (immediate)
**Purpose:** Ask probing questions that reveal hidden assumptions.
**Runs:** Immediately after any deliverable.
**How:** Asks 3-5 targeted questions: "What happens when X is null?", "What if the network is slow?", "How does this handle concurrent access?" If the role cannot answer, the finding is logged.
**Return:** {critic, target, verdict: pass/fail, findings: [{category, severity, detail}], evidence: "question-and-answer", confidence: 0-1}

### 5. regression-gate (gapped)
**Purpose:** Ensure no existing functionality was broken.
**Runs:** 2 runs delayed (next run's test phase).
**How:** Compares the current test results against the previous run's test results. Reports any test that was passing and is now failing.
**Return:** {critic, target, verdict: pass/fail, findings: [{category, severity, detail}], evidence: "test-name", confidence: 0-1}

## Gapped execution model

Gapped critics run on the NEXT run, not the current one:

```
Run N:  spec-integrity reviews Run N-2's diff
        oracle reviews Run N-2's tests
        regression-gate reviews Run N-2's test results
```

This means:
- First 2 runs have no gapped critic feedback (bootstrap period)
- After 2 runs, all 5 of the original critics (spec-integrity, oracle, implementation, socratic-quality, regression-gate) are active — role-adherence isn't gapped, so it runs from the first deliverable regardless of bootstrap
- Findings from gapped critics are added to the NEXT run's brief

## 3-pass / 3-fail auto-tuning

### 3 consecutive passes (auto-approve)
If a critic passes 3 consecutive times on the same type of deliverable:
1. Skip that critic for the next run
2. Log: "auto-approved: [critic] passed 3 consecutive runs"
3. Resume normal evaluation after 5 runs or when a drift alert triggers

### 3 consecutive failures (mandatory re-work)
If a critic fails 3 consecutive times on the same type of deliverable:
1. Mandatory re-work before proceeding
2. Atlas-lead creates a drift alert in lessons.md
3. Drift alert is included in future delegation briefs
4. Only the user can waive the re-work requirement

## Structured critic output

All critics return JSON:
```json
{
  "critic": "spec-integrity",
  "target": "requirements.md (section 3)",
  "verdict": "fail",
  "findings": [
    {
      "category": "missing-scenario",
      "severity": "high",
      "detail": "No acceptance criteria for concurrent user access"
    }
  ],
  "evidence": "requirements.md:45-52",
  "confidence": 0.85
}
```

## Integration with trajectory logging

Critic verdicts get one plain JSONL entry each, per `knowledge/process/trajectory-logging.md` — no fabricated tracing spans, just the fields that schema already defines:
```json
{"ts": "2026-07-22T14:30:00Z", "role": "atlas-lead", "action": "gate-check", "target": "spec-integrity", "outcome": "failure", "why": "2 findings, high severity"}
```

## Anti-patterns

- Running all 5 opt-in critics on every small task (use the subset appropriate to variant; role-adherence is cheap enough to always run)
- Ignoring critic findings because "it's probably fine"
- Having the same role that produced the deliverable also run the critic (critics must be isolated)
- Skipping critics during "fast iteration" (that's when you need them most)
