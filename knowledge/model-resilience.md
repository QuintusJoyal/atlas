# Model resilience and automatic downgrade

Canonical reference for keeping the workflow running when a model is quota-limited or unavailable. The user wants no interruptions for this. Roles and atlas-lead downgrade automatically, continue, log, and inform. They do not stop to ask.

## Tier cascade

Retry the affected step at the next tier down, in order:

| From | To |
| --- | --- |
| claude-opus-4-8-thinking-high | composer-2.5 |
| composer-2.5 | composer-2 |
| composer-2 | inherit |
| inherit | (exhausted: address the user) |

IDE Task/subagent and agent frontmatter use **IDE slugs** (e.g. `composer-2.5-fast`, `claude-opus-4-8-thinking-high`). The Cursor SDK `Agent.create` API only accepts ids from `Cursor.models.list()`. The Control Center SDK runner resolves aliases at runtime via `models.ts` `resolveModel()` in [`atlas-control-center/sdk/`](https://github.com/QuintusJoyal/atlas-control-center/tree/main/sdk) before every `Agent.create` call.

| IDE / frontmatter slug | SDK slug (`Agent.create`) | Tier |
| --- | --- | --- |
| claude-opus-4-8-thinking-high | claude-opus-4-8 | premium |
| claude-opus-4-7-thinking-medium | claude-opus-4-7 | premium (Task only) |
| composer-2.5 | composer-2.5 | standard |
| composer-2.5-fast | composer-2.5 | fast (IDE "Composer Fast") |
| composer-2 | composer-2 | fast |
| inherit | default | inherit |

Agent frontmatter and rules keep IDE slugs for documentation and IDE Task parity. Do not change every `agents/*.md` file; runtime resolution in the Control Center SDK (`atlas-control-center/sdk/models.ts`) is preferred.

## Task tool: starting model and invoke cascade

The Task tool accepts only a **small set of model slugs**. Agent frontmatter may say `composer-2.5` or `composer-2`; map those to a valid Task slug before the first call.

| Role frontmatter `model:` | Task `model` param (first try) |
| --- | --- |
| `claude-opus-4-8-thinking-high` | `claude-opus-4-8-thinking-high` |
| `composer-2.5` | `composer-2.5-fast` |
| `composer-2` | `composer-2.5-fast` |
| (unset / inherit) | omit `model` or `composer-2.5-fast` |

When a Task call **fails to execute** (tool error before or instead of a subagent run), atlas-lead **must re-trigger in the same turn** with the next model on this cascade. Do not stop after one failed invoke.

| Step | Task `model` | When to use |
| --- | --- | --- |
| 1 | Role-mapped slug from table above | First attempt |
| 2 | `claude-opus-4-8-thinking-high` | After step 1 failed (if not already step 1) |
| 3 | `claude-opus-4-7-thinking-medium` | After step 2 failed |
| 4 | `composer-2.5-fast` | After step 3 failed |
| 5 | *(omit `model`)* | After step 4 failed (inherit) |
| 6 | (none) | All failed: address the user |

**Invoke failure** includes: invalid or unavailable `model`, quota/rate-limit on Task launch, "Invalid arguments", usage-limit messages on the Task tool, and empty/error returns with no subagent output.

**Procedure (same turn):**

1. Keep `subagent_type`, `description`, and `prompt` unchanged (same brief).
2. Log: `downgrade: <role> Task invoke <from> to <to>, reason <quota|unavailable|invalid-model|blocked>, run <id>, date <when>`.
3. Call Task again immediately with the next `model` in the table.
4. Only after step 5 fails may lead stop and tell the user to invoke `/atlas-<role>` directly or start a fresh chat.

**Subagent_type not in Task enum:** If `subagent_type="atlas-<role>"` fails with an invalid enum, retry once with `subagent_type="generalPurpose"`, same `description`, prompt prefixed with `You are <role>. …`, and continue the **same model cascade** on each failure. This is a launch fallback, not permission for lead to work inline.

**Subagent ran then failed:** Use the tier cascade at the top of this doc (subagent quota mid-run), still re-delegate with the next Task `model` in the same turn when the failure is reported in that turn.

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
4. If every tier including `inherit` is exhausted, stop and address the user with what failed and the options.

## Orchestrator: re-delegate as a team

Atlas is a **team**, not a single agent. When usage limits interrupt a step, **atlas-lead re-delegates to the same named role at a lower tier**. Lead does not absorb the work.

### When atlas-lead itself hits the limit (most common)

User-reported failure mode: **the orchestrator session** runs out of quota, then lead does everything inline. This is always wrong.

Lead runs on **standard** tier by default so premium quota stays for gate roles (architect, security, reviewer) via Task. Even when **your** session is limited:

1. **Keep delegating via Task.** Subagents run on their own model allocation. Your limit is not the team's limit.
2. **Your next turn should be Task call(s)**, not implementation, specs, or tests in this thread.
3. **Delegate early** in the pipeline (first or second turn) so lead quota is not spent on long monologues before Task.
4. **Never collapse** into solo work because "I'm at limit" or "delegation overhead is too expensive."
5. **If Task is also blocked:** stop and tell the user to invoke `/atlas-<role>` directly or open a fresh chat. Do not substitute.

Log: `downgrade: atlas-lead <from-tier> to <to-tier>, reason quota, run <run-id>, date <when>`.

### When to re-delegate (subagent failed)

Re-delegate (same role, lower model) when:

- A Task subagent fails or returns incomplete work with quota, rate-limit, unavailable, or blocked errors.
- A delegation was interrupted mid-run (usage cap, model unavailable, subagent error tied to model access).
- Lead's own coordination call hits a limit (downgrade lead only for routing and summaries, never to do specialist work).

### Re-delegation procedure (atlas-lead)

1. **Identify** the affected role and its starting tier (agent frontmatter `model:` or the tier table in `README.md`).
2. **One short retry** at the same tier if the error looks transient (rate limit).
3. **Downgrade one step** on the tier cascade. Do not skip tiers.
4. **Re-launch Task** with the **same brief** and the same `subagent_type` (e.g. `atlas-architect`). Pass `model: <downgraded-tier>` when the Task tool accepts it; otherwise put the tier in the brief header.
5. **Keep `team.json` current**: role stays `active`; set `note` to `downgraded <from>→<to>, re-delegated`; set `model` and `downgradedFrom` when present.
6. **Log** in `budget.md` and `usage-insights.md` per the logging format below.
7. **Continue the pipeline**: the next role still starts at its **default** tier. For parallel delegations, retry only the failed role; do not restart the whole roster.
8. **Summarize** downgrades for the user in the next handoff. Flag premium gate roles.

### What lead must never do on quota failure

- Produce the specialist deliverable inline ("I'll finish the design since opus failed").
- Skip Task and run the next phase as lead.
- Use Write, StrReplace, or Shell to implement, test, or specify on behalf of the failed role.
- Treat token-budget "resume" as permission to work solo. Resume means re-delegate via Task.
- Stop the entire pipeline unless **every** tier including `inherit` is exhausted for that role.

### Common failure mode (user-reported)

**Lead itself hits quota** → lead tries to do everything directly in the same chat. **Always wrong.** Lead's next action is Task to the owning role(s). Subagents do the work even when lead is throttled.

Secondary failure: Task subagent fails → lead inlines instead of re-delegating. Fix: Task again at lower tier.

### Direct role invocation (no lead)

When the user invokes `/atlas-<role>` directly, that role downgrades **within its own session**: retry the same step at the next tier without asking. It does not hand work to atlas-lead unless the user asks for orchestration.

## Logging format

Record each downgrade in the run `budget.md` and append to `usage-insights.md`:

```
- downgrade: <role> <from-tier> to <to-tier>, reason <quota|rate-limit|unavailable|blocked>, run <run-id>, date <when>
```

## Quality flag

If a premium gate role (atlas-security, atlas-reviewer, atlas-architect) ran downgraded, flag it in the handoff and final summary so the user can re-run that gate at full tier if they want. The flag is informational and does not block delivery.
