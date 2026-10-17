---
name: token-budget-enforcement
category: process
load-when: Predicting heavy tasks, loading knowledge, handing off, debugging context overflow, lite-mode work
skip-when: Trivial single-step tasks with no knowledge loading
description: Programmatic-style enforcement of knowledge-loading token budgets. Counting checkpoints, tier caps, and truncation rules that turn budgets from guidelines into constraints.
audience: [atlas-lead, all]
tags: [tokens, budget, enforcement, context, caching, lite]
---

# Token budget enforcement

Atlas token budgets were prompt-enforced guidelines. This document makes them explicit constraints with counting checkpoints and a defined exceeded-budget path.

The enforcement is still prompt-based (there is no runtime token counter yet), so it depends on agents honoring the checkpoints. The point is to remove ambiguity: every load has a number attached and a rule for what to do when the number is crossed.

## Quick Reference
- Three tiers: routine, complex, hard cap
- Count at every tier boundary — before loading, after loading
- Exceeded budget: truncate to summary, log a warning, continue with reduced context
- Never silently drop a required fact to save tokens — degrade gracefully
- Budget overruns must stay visible in the trajectory log and handoff

## Budget tiers

| Tier | Knowledge loading budget | Typical trigger | Composition |
|------|--------------------------|-----------------|-------------|
| Routine | 400-600 tokens | Known task, clear scope | 2-3 searches, no full file |
| Complex | 1,500-2,500 tokens | Unusual task, cross-domain | 3-5 searches + 1 full file |
| Hard cap | 5,000 tokens | Absolute ceiling per task | Never exceeded by design |

These match the budgets in `rules/atlas-core.md` and `knowledge/benchmark/performance-benchmarks.md`. The hard cap is not a target; it is the point at which loading stops and truncation begins.

Output tokens cost 3-5x input tokens, so the same discipline applies to responses: see the output-length limits in `rules/atlas-core.md`.

## Counting checkpoints

Token counts here are estimates. A rough heuristic: **1 token ≈ 4 characters** of English prose, or ~0.75 words. Use it consistently so numbers are comparable across a run.

Count at four points:

1. **Predict** — before the first load, classify the task tier and state the budget. For heavy tasks this feeds the token-budget gate.
2. **Before each load** — estimate the incoming search result or file and check it fits the remaining budget. If it would cross the cap, take the partial path below instead of loading.
3. **After each load** — add the actual estimate to a running total. Track it like any other piece of state.
4. **At handoff/phase end** — record the total in the trajectory log (see `knowledge/process/trajectory-logging.md`) and carry it in the handoff so the receiving role does not reset the count.

Stop loading once the tier budget is spent. A routine task that has used 600 tokens does not get to "just grep one more thing" — that is budget creep, and it is exactly what this enforcement prevents.

## Exceeded-budget handling

When a load would cross the hard cap, or a tier is already spent and more context seems needed:

1. **Truncate to summary.** Do not load the full artifact. Load the smallest slice that answers the question: a single grep line, a section heading plus its first paragraph, or a short paraphrase. Record what was summarized.
2. **Log a warning.** Append a trajectory entry with `action: "budget"`, `outcome: "exceeded"`, the tier, the running total, and what was truncated. A silent overrun is a bug.
3. **Continue with reduced context.** Do not stop the task. Work with what fits. If a required fact is genuinely unreachable within the cap, escalate (T2) rather than blowing the budget — an escalation is cheaper than an unbounded load.

Prefer degradation over overflow: a summarized fact plus an explicit "truncated, verify before relying" note is better than silently loading everything and eroding the token economy.

## Lite mode (8K context)

Lite mode runs on 8K windows. The full-bundle hard cap (5,000) is too large a fraction of that budget once the system prompt, task state, and tool output are counted. Lite budgets are tightened accordingly:

| Tier | Lite budget | Notes |
|------|-------------|-------|
| Routine | 200-300 tokens | Playbook inline only, no external load |
| Complex | 500-800 tokens | At most one small excerpt |
| Hard cap | 1,000 tokens | Absolute ceiling |

Lite mode does not load external `knowledge/` files. If a task needs more than the playbook plus ~1,000 tokens of excerpt, it is outside lite mode's scope: tell the user and suggest the full bundle. On an 8K window, an overload does not degrade gracefully — it overflows. When in doubt, load less and escalate sooner.

## Cache stability

Budget enforcement and prefix caching are the same problem from two directions (see `knowledge/context/prompt-cache-strategy.md`). Unbounded loading changes the dynamic tail every turn, which keeps evicting the cacheable prefix. Capping what loads keeps the prefix stable and the tail predictable.

Rules that follow from this:
- Static rules stay in the system prompt; dynamic knowledge loads as context.
- Load order is stable across turns for the same task tier.
- Do not re-load a file already loaded this session. Reuse the earlier excerpt; a re-load pays the full cost again and can shift the prefix.
- A budget-exceeded truncation is preferable to a variable full load, because it keeps the tail small and repeatable.

## Trajectory integration

Every enforcement event is observable. Extend the standard trajectory entry (see `knowledge/process/trajectory-logging.md`) with:

| Field | Meaning |
|-------|---------|
| `budgetTier` | routine / complex / hard-cap / lite |
| `tokensLoaded` | Running total after this action |
| `budgetExceeded` | true when the action crossed the tier or cap |
| `truncatedTo` | What was summarized instead of loaded (when exceeded) |

Aggregating `tokensLoaded` per role shows which roles drift over budget. That drift is the input to the next budget revision, not a reason to raise the cap mid-run.

## Anti-patterns
- Loading a full file "because it might be relevant" when a grep line would answer the question
- Resetting the running total at each handoff (the receiving role inherits the spend)
- Silently dropping context at the cap with no trajectory warning
- Raising the cap mid-task instead of truncating or escalating
- Treating the hard cap as the routine budget
