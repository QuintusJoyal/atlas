---
name: model-resilience
category: process
description: Canonical reference for automatic model downgrade and tier cascade when quota limits or availability issues occur.
audience: [atlas-lead, all]
tags: [model-tiers, resilience, downgrade, quota]
---

# Model resilience and automatic downgrade

Canonical reference for keeping the workflow running when a model is quota-limited or unavailable. The user wants no interruptions for this. Roles and atlas-lead downgrade automatically, continue, log, and inform. They do not stop to ask.

## Tier cascade

Retry the affected step at the next tier down, in order:

| From | To |
| --- | --- |
| premium | standard |
| standard | fast |
| fast | (exhausted: address the user) |

Each IDE maps tiers to its available models. The `modelHints` field in agent frontmatter provides per-IDE suggestions. The exact model used depends on the IDE's runtime.

## Delegation: starting tier and cascade

When atlas-lead delegates to a specialist role, it uses the role's assigned tier. If the delegation fails to execute (invalid model, tool error, quota at launch), atlas-lead **must re-delegate in the same turn** with the next tier on the cascade.

| Step | Tier | When to use |
| --- | --- | --- |
| 1 | Role-assigned tier | First attempt |
| 2 | premium | After step 1 failed (if not already premium) |
| 3 | standard | After step 2 failed |
| 4 | fast | After step 3 failed |
| 5 | (none) | All failed: address the user |

**Invoke failure** includes: invalid or unavailable model, quota/rate-limit on delegation launch, "Invalid arguments", usage-limit messages on the delegation tool, and empty/error returns with no output.

**Procedure (same turn):**

1. Keep the target role, title, and brief unchanged (same delegation payload).
2. Log: `downgrade: <role> delegation invoke <from> to <to>, reason <quota|unavailable|invalid-model|blocked>, run <id>, date <when>`.
3. Re-delegate immediately with the next tier in the cascade.
4. Only after all tiers fail may lead stop and tell the user to invoke the role directly or start a fresh chat.

**Role not recognized:** If delegation to `atlas-<role>` fails, retry once with a generic orchestrator role and prefix the brief with `You are <role>. …`, then continue the same tier cascade. This is a launch fallback, not permission for lead to work inline.

**Subagent ran then failed:** Use the tier cascade (subagent quota mid-run), still re-delegate with the next tier in the same turn when the failure is reported.

## Triggers

Downgrade when a model call fails for any of these reasons:

- Quota or usage limit reached for the tier.
- Rate limit or throttling that does not clear on a short retry.
- Model unavailable, blocked by policy, or not on the account or plan.
- A retryable startup failure tied to model access.

For a transient rate limit, one short retry at the same tier is fine first. If it persists, downgrade.

## Behavior

1. Apply the downgrade only to the affected step. Retry the same brief at the next tier.
2. Continue the workflow. Never block or ask permission to downgrade.
3. Start the next step at its own assigned tier. The limit may have cleared.
4. If every tier is exhausted, stop and address the user with what failed and the options.

## Orchestrator: re-delegate as a team

Atlas is a **team**, not a single agent. When usage limits interrupt a step, **atlas-lead re-delegates to the same named role at a lower tier**. Lead does not absorb the work.

### When atlas-lead itself hits the limit (most common)

User-reported failure mode: **the orchestrator session** runs out of quota, then lead does everything inline. This is always wrong.

Lead runs on **standard** tier by default so premium quota stays for gate roles (architect, security, reviewer) via delegation. Even when **your** session is limited:

1. **Keep delegating.** Subagents run on their own model allocation. Your limit is not the team's limit.
2. **Your next turn should be delegation call(s)**, not implementation, specs, or tests in this thread.
3. **Delegate early** in the pipeline (first or second turn) so lead quota is not spent on long monologues before delegation.
4. **Never collapse** into solo work because "I'm at limit" or "delegation overhead is too expensive."
5. **If delegation is also blocked:** stop and tell the user to invoke the role directly or open a fresh chat. Do not substitute.

Log: `downgrade: atlas-lead <from-tier> to <to-tier>, reason quota, run <run-id>, date <when>`.

### When to re-delegate (subagent failed)

Re-delegate (same role, lower model) when:

- A subagent fails or returns incomplete work with quota, rate-limit, unavailable, or blocked errors.
- A delegation was interrupted mid-run (usage cap, model unavailable, subagent error tied to model access).
- Lead's own coordination call hits a limit (downgrade lead only for routing and summaries, never to do specialist work).

### Re-delegation procedure (atlas-lead)

1. **Identify** the affected role and its starting tier (agent frontmatter `tier:` or the tier table in `README.md`).
2. **One short retry** at the same tier if the error looks transient (rate limit).
3. **Downgrade one step** on the tier cascade. Do not skip tiers.
4. **Re-delegate** with the **same brief** and the same target role (e.g. `atlas-architect`). Pass the downgraded tier in the brief header.
5. **Keep `team.json` current**: role stays `active`; set `note` to `downgraded <from>→<to>, re-delegated`; set `tier` and `downgradedFrom` when present.
6. **Log** in `budget.md` and `usage-insights.md` per the logging format below.
7. **Continue the pipeline**: the next role still starts at its **default** tier. For parallel delegations, retry only the failed role; do not restart the whole roster.
8. **Summarize** downgrades for the user in the next handoff. Flag premium gate roles.

### What lead must never do on quota failure

- Produce the specialist deliverable inline ("I'll finish the design since opus failed").
- Skip delegation and run the next phase as lead.
- Implement, test, or specify on behalf of the failed role.
- Treat token-budget "resume" as permission to work solo. Resume means re-delegate.
- Stop the entire pipeline unless **every** tier is exhausted for that role.

### Common failure mode (user-reported)

**Lead itself hits quota** → lead tries to do everything directly in the same chat. **Always wrong.** Lead's next action is delegation to the owning role(s). Subagents do the work even when lead is throttled.

Secondary failure: subagent fails → lead inlines instead of re-delegating. Fix: delegate again at lower tier.

### Direct role invocation (no lead)

When the user invokes a role directly, that role downgrades **within its own session**: retry the same step at the next tier without asking. It does not hand work to atlas-lead unless the user asks for orchestration.

## Logging format

Record each downgrade in the run `budget.md` and append to `usage-insights.md`:

```
- downgrade: <role> <from-tier> to <to-tier>, reason <quota|rate-limit|unavailable|blocked>, run <run-id>, date <when>
```

## Quality flag

If a premium gate role (atlas-security, atlas-reviewer, atlas-architect) ran downgraded, flag it in the handoff and final summary so the user can re-run that gate at full tier if they want. The flag is informational and does not block delivery.

## Frontier behavior patterns

These patterns keep agents efficient when running on models with limited context windows or tool budgets.

### Context compaction

When context usage exceeds ~80% of the model window:

1. Summarize completed work into a compact state block: current phase, owned artifacts, delegation status, open questions.
2. Discard verbose tool outputs (full file contents, detailed logs) and retain only paths, line references, and key findings.
3. Continue the current task without restart. The state block replaces raw history.
4. If compaction is not enough (still over budget), delegate the remaining work to a fresh session with the compact state as the brief.

**Never lose:** current task goal, owned artifact paths, delegation state in `team.json`, user decisions, and open blockers.

### When to compact vs. when not to compact

| Compact when | Don't compact when |
|---|---|
| A sub-task is resolved (test written, design approved, etc.) | Mid-derivation (reasoning chain in progress) |
| Context exceeds ~80% of the model window | Active exploration (grep/glob in flight) |
| Switching phases (design → implementation) | Waiting for user input (hold state as-is) |
| Returning from a long subagent run | Early in a turn (under 50% context) |
| Starting a new delegation cycle | During a pre-action gate checklist |

**Proactive compaction:** don't wait for the context window to fill. After completing a significant unit of work (artifact delivered, gate passed, phase transition), proactively summarize what was done and what remains. Write the summary to the state block before starting the next unit.

### Tool clearing

When switching between phases or roles:

1. Release file handles and MCP connections that are no longer needed for the next step.
2. Do not hold stale locks across unrelated delegations.
3. Before starting a new phase, confirm only relevant tools are loaded (e.g., do not keep a test runner loaded during design work).

### Structured output

All handoffs and artifacts should use structured markdown:

- **Handoffs:** use the handoff protocol format. No prose dumps.
- **Delegation briefs:** use the brief structure (Goal, Background, Project, Inputs, Scope, Deliverable, Questions).
- **Status updates:** use tables or bullet lists, not paragraphs.
- **Error reports:** include role, tier, error type, and next action — not a wall of text.

### Output length targets

| Output type | Target tokens | Max tokens |
| --- | --- | --- |
| Delegation brief | 500–1,000 | 1,500 |
| Handoff artifact | 300–600 | 1,000 |
| Status summary | 200–400 | 600 |
| Lead orchestration turn | 500–1,500 | 4,000 |
| Specialist implementation turn | 1,000–2,000 | 4,000 |

These are targets, not hard limits. Artifact content (code, tests, ADRs) may exceed them when the work requires it.
