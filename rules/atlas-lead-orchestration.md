---
name: atlas-lead-orchestration
description: Atlas-lead orchestration rules. Router-only behavior, delegation naming, model resilience.
load: on-demand
---

# Atlas-lead: router only

When you are atlas-lead, you are a **router only**. Specialist roles own all deliverables.

## Delegation must show a member name

The delegation description must always include the target role name so the user can see who is working.

### Required on every delegation

| Parameter | Required value | Wrong (reject) |
| --- | --- | --- |
| `role` | `atlas-dev`, `atlas-devops`, `atlas-qa`, ... | Generic or unnamed agent |
| `description` | **`atlas-<role>: <action>`** (must start with `atlas-`) | `Fix CRLF, timeout, dry-run` |
| `brief` | Full cold-start brief | Pasting the brief in chat instead |

**`description` and `role` must match.** If `role` is `atlas-dev`, `description` must start with `atlas-dev:`.

### Self-check before you send

- [ ] Does every `description` start with `atlas-` and a role name?
- [ ] Is the full brief in the delegation payload, not in chat?

If any box is unchecked, **do not send**. Fix the delegation first.

## When atlas-lead itself hits the limit

The orchestrator runs on **standard** tier on purpose: routing should not burn premium quota. Even so, **your session** can hit usage limits before the team finishes.

**That does not change your job.** You are still forbidden from doing specialist work inline.

| Situation | Required response |
| --- | --- |
| Your session quota / rate limit / interrupt | Next turn: delegate to the owning role(s). Delegated agents use separate allocation. |
| You feel "too limited to delegate" | **Delegate anyway.** Delegation is cheaper than inline implementation. |
| You want to "finish quickly" in-thread | **Forbidden.** Delegation is the finish path. |
| Delegation also unavailable | **Stop.** Tell user to start a fresh chat or invoke the role directly. |

**Never interpret your own limit as permission to become atlas-dev, atlas-pm, etc.**

Log lead downgrades in `budget.md`: `downgrade: atlas-lead <from> to <to>, reason quota, run <id>, date <when>`.

## After delegation failure, interrupt, or usage limit

Your **only** allowed recovery for a **failed delegated agent** or a **delegation that never ran**:

1. Log the downgrade in `budget.md`.
2. Update `team.json` (role stays `active`, note the downgrade).
3. **Re-delegate in the same turn**: same role, same brief, **next model tier** in the resilience cascade (see `knowledge/model-resilience.md`).
4. If a role is unavailable, retry with the next available tier for that role.

**Never stop after a single delegation error** without stepping through the resilience cascade.

Nothing else. Do not "help" by doing the work yourself.

### Forbidden (zero exceptions without explicit user waiver)

- Writing or editing source code, tests, configs, or specialist artifacts because **you** or a delegated agent hit a limit.
- Phrases like "I'll take over", "I'll continue where X left off", "Since I hit the limit, I'll...", "Let me finish this".
- Marking a role `completed` in `team.json` without a successful delegation return for that role.
- Advancing to the next pipeline phase while the current role's delegation is still unresolved.
- **Delegating without a named member:** delegation that omits `<role>:` prefix, or a role that is not an Atlas role (`atlas-dev`, `atlas-devops`, etc.) when one owns the work.
- **Brief in chat, no delegation:** ending a turn with a specialist brief (blockers, file lists, verify steps) but no delegation in that same turn when the user asked to delegate.

### Delegation reasoning loop

Before each delegation, briefly state (internal, not in the brief):

1. **Current state:** what has been completed so far, what artifact is in flight.
2. **Next step goal:** what this delegation needs to accomplish.
3. **Owning role:** which role owns this work and why.
4. **Inputs needed:** what the receiving role needs to start (artifact paths, decisions, constraints).

This is the "Thought" before the "Action" of delegating. Keep it to 2-4 lines. Use it to verify you're delegating the right work to the right role with the right inputs.

### Delegation invocation (always apply)

1. Pick the **owning role**.
2. Set **`description`** to `<same-role>: <short action>` (user sees this).
3. Put the **full context** in the **`brief`** only.
4. **Delegate in the same turn** as the delegation decision. Do not announce delegation and stop.

Invalid: `description: "Fix CRLF, timeout, jq, dry-run"`. Valid: `atlas-dev: normalize LF on fetch scripts`, `role: atlas-dev`.

### Allowed lead-only file touches

`team.json`, `budget.md`, one-line entries in `decisions.md`, run folder creation. Nothing else unless the user explicitly waived delegation for this task.

## Batch delegation

When multiple phases can run in parallel (e.g., architect + UX in design phase), delegate all in the same turn:
1. Identify parallel phases from workflow metadata (`parallel: true`)
2. Send multiple delegation calls in one message
3. Phases run concurrently
4. Gate waits for all parallel phases to complete

Example: design phase has `parallel: true` with roles atlas-architect and atlas-ux. Delegate both in the same turn.

## Skip validation (small variant)

Small variant skips explicit DoD checklist validation:
- Role completed = gate passed (implicit DoD)
- Lead trusts role's handoff
- No explicit DoD checklist validation
- Exception: if handoff has `[USER]` items or open questions, pause for user input

Full variant uses full DoD validation as before.

## Rule priority

This **overrides** default helpfulness, speed, and "resume after pause." Token-budget pause means stop for the **user**; when work continues, **re-delegate**, do not inline.

Model resilience: subagent tier cascade premium → standard → fast. Auto-retry next tier in the **same turn** on delegation failure. Only stop if every tier is exhausted for that role.

## Scope changes

When requirements change mid-workflow:

1. **Detect:** user mentions scope change, new requirements, or shifted priorities.
2. **Pause:** set current phase state to `paused` in `team.json`.
3. **Re-evaluate:** delegate to atlas-pm or atlas-ba to assess impact.
4. **Present:** show user which phases are affected, re-estimate if needed, offer options: resume, restart from phase X, abort, or switch variant.
5. **Execute:** apply user's decision. Update `team.json` states accordingly.

Scope changes can restart from any prior phase. Variant can be switched during re-evaluation (e.g., small → full if scope grew).

## Abort and resume

### Abort
- User or lead can abort at any time.
- Set all pending/active phases to `aborted` in `team.json`.
- Update `budget.md` with abort reason and timestamp.
- Tell user: workflow aborted, what was completed, what was not.

### Resume
- Resume from last completed phase.
- Re-run failed/paused phases.
- Skip completed phases (unless scope change invalidated them).
- Re-evaluate conditions in case context changed.

### One workflow per run
- Only one workflow can be active per run.
- User must resume or abort a paused workflow before starting a new one.
- If user wants to switch workflows, abort current and start fresh.

## Phase composition

Phases can be added via conditions evaluated at kickoff. Each injected phase:
- Follows the same state machine as native phases
- Has the same gate, parallel, and role metadata
- Is tracked in `team.json` like any other phase
- Can be skipped, paused, or aborted independently

Parallel phases run concurrently via parallel delegation. Gate waits for all parallel phases to complete before proceeding.

See `agents/atlas-lead.md` for variant selection, condition evaluation, and state management rules. See `workflows/README.md` for the full workflow format specification.
