---
name: self-healing-protocol
category: process
load-when: A role fails, times out, hits quota, loops without progress, or a session runs out of context
skip-when: Normal step execution with no failure or degradation
description: Runtime self-healing and recovery for Atlas agents. Retry with backoff, context compaction, tier fallback, stuck-agent kill-and-respawn, checkpointed partial results.
audience: [atlas-lead, all]
tags: [self-healing, recovery, retry, backoff, fallback, stuck, checkpoint, degradation]
---

# Autonomous self-healing and recovery

Atlas keeps a workflow running when a role fails, a model is throttled, context fills, or an agent loops without progress. This is the programmatic layer under the prompt-only guidance in `knowledge/reference/model-resilience.md` and `knowledge/process/checkpoint-protocol.md`. It is enforced by `scripts/self-healing.py`, which the host integration calls around model and tool invocations.

The default posture is the same as model resilience: recover, continue, log, inform. Do not stop to ask unless every recovery path is exhausted.

## Quick reference

| Failure | Recovery |
| --- | --- |
| Timeout, transient error, short rate limit | Retry with exponential backoff (max retries configurable) |
| Context reaches 75% of the window | Compact completed phases into a state block |
| Quota or rate limit that persists past one retry | Cascade one tier down: premium, standard, fast |
| Same agent state for N turns | Kill and respawn from the last checkpoint |
| Phase completes | Save an atomic checkpoint to disk |
| Agent fails with partial work done | Preserve partial results, re-delegate the remaining scope only |

All behaviors are feature-flagged through `ATLAS_SELF_HEALING_*` environment variables so they can be rolled out incrementally. `ATLAS_SELF_HEALING=0` disables the runtime.

## Failure classification

Every failure is classified before recovery so the right path is chosen. The categories extend the structured error contract in `knowledge/process/aci-enforcement.md`.

| Category | Examples | Recovery path |
| --- | --- | --- |
| `transient` | timeout, connection reset, 502/503/504, temporarily unavailable | Retry with backoff |
| `rate-limit` | 429, throttled, too many requests | One short retry, then tier cascade |
| `quota` | usage limit, credits, context length | Tier cascade |
| `validation` | invalid or malformed argument | Do not retry; fix the call or escalate |
| `permission` | 403, denied, not allowed | Do not retry; escalate (MCP writes need approval) |
| `not-found` | no such file, 404 | Do not retry; re-resolve the target |
| `business` | any other deterministic failure | Do not retry; escalate to atlas-lead |

Classification matters because retrying a validation or permission error just burns budget, and cascading on a validation error is exactly the ambiguous-quota thrash the rollout risk calls out.

## Retry with exponential backoff

Retry only `transient`, `rate-limit`, and timeout failures. Backoff is `base_delay * 2^(attempt-1)`, capped at `max_delay`.

| Attempt | Delay (default) |
| --- | --- |
| 1 | 1s |
| 2 | 2s |
| 3 | 4s |
| 4+ | capped at 30s |

Defaults: 3 retries, 1s base, 30s cap. Configure with `ATLAS_SELF_HEALING_MAX_RETRIES`, `ATLAS_SELF_HEALING_BASE_DELAY`, and `ATLAS_SELF_HEALING_MAX_DELAY`. After the retries are exhausted, a `rate-limit` or `quota` failure moves to the tier cascade; anything else escalates.

This replaces the hardcoded `1s, 2s, 4s` line in `knowledge/process/runtime-execution.md` with a configurable policy.

## Context compaction trigger

Compact when context usage reaches 75% of the model window (`ATLAS_SELF_HEALING_COMPACT_AT`, default `0.75`). This is the early trigger, ahead of the ~80% hard compaction in `rules/atlas-core.md`.

On trigger:

1. Summarize completed phases into the state block in `knowledge/reference/model-resilience.md` and write it to `$ATLAS_DATA_DIR/runs/<run-id>/state.md`.
2. Keep current task, owned artifact paths, delegation state, user decisions, and open blockers. Drop verbose tool output.
3. Continue without restart. If still over budget, save a checkpoint and delegate the remaining work to a fresh session using the Fresh Session Brief template.

## Tier fallback cascade

On a `quota` or persistent `rate-limit` failure, downgrade exactly one step: premium, standard, fast. Do not skip tiers. Re-delegate the same role with the same brief at the next tier, in the same turn, per `knowledge/reference/model-resilience.md`.

**Cooldown:** when a tier fails, it is parked for `ATLAS_SELF_HEALING_COOLDOWN` seconds (default 600). While parked it is not re-offered, so an ambiguous quota error cannot bounce the agent up and down. When every remaining tier is cooling down, the cascade is exhausted: stop and address the user, exactly as model resilience specifies.

Cascading is never permission for atlas-lead to do the specialist work inline. It stays delegation.

Log each step:

```
downgrade: <role> to <tier>, reason <quota|rate-limit|unavailable|blocked>, date <when>
```

## Stuck-agent detector and kill-and-respawn

An agent is stuck when its observable state does not change for N consecutive turns. State fingerprint: current phase, owned artifact paths, `team.json` status for the role, and the trajectory tail.

Default threshold: 5 turns (`ATLAS_SELF_HEALING_STUCK_TURNS`). On detection:

1. Stop the stuck agent (kill the run or subagent).
2. Load the role's most recent checkpoint from `$ATLAS_DATA_DIR/checkpoints/`.
3. Respawn the role with the checkpoint state plus a one-line note that the previous run made no progress, so it does not repeat the same approach.
4. Log the kill-and-respawn in `trajectory.jsonl`.

A real state transition resets the counter. Before killing, confirm no side-effecting tool call is in flight; if one is, let it settle or roll it back first so a respawn cannot double-apply a write.

## Checkpoint serialization

Save a checkpoint at every phase completion (and before risky operations), matching `knowledge/process/checkpoint-protocol.md`. `scripts/self-healing.py` writes JSON checkpoints to `$ATLAS_DATA_DIR/checkpoints/` using a temp file plus atomic rename, so a crash mid-write can never corrupt the previous good checkpoint.

Each file is versioned with `schema: atlas-recovery/1.0` and carries `checkpointId`, `role`, `phase`, `level`, `created`, and a `state` object (current task, owned artifacts, pending decisions, delegation state, budget). `latest(role)` returns the newest checkpoint for a role; that is what kill-and-respawn restores from.

## Graceful degradation

When a role fails with work already done, do not restart the phase from zero. Build a degradation report:

- `partialResults.preservedArtifacts`: what the failed role finished and left on disk.
- `partialResults.remainingScope`: the work that is still outstanding.
- `checkpointId`: the checkpoint to respawn from, if the role will continue.
- `redelegate.scope`: `remaining only`.

atlas-lead re-delegates the remaining scope to the same role (or the next tier down). Completed artifacts are trusted and not redone. If the remaining scope needs a different role, lead delegates to that role with the preserved artifacts as inputs.

## Runtime reference

`scripts/self-healing.py` is stdlib-only and importable, or runnable for its checks:

```
python3 scripts/self-healing.py --self-test          # verify the recovery primitives
python3 scripts/self-healing.py --self-test --verbose
```

| Function | Purpose |
| --- | --- |
| `classify_error(message)` | Failure category for routing |
| `RetryPolicy`, `run_with_retry(fn)` | Exponential backoff retry |
| `should_compact(tokens, window)` | 75% compaction trigger |
| `TierCascade` | premium to standard to fast with cooldown |
| `StuckDetector` | no-progress detection |
| `CheckpointStore` | atomic, versioned checkpoint save/load/latest |
| `degradation_report(...)` | partial-results bundle for re-delegation |

## Rollout

Enable one behavior at a time. Retry and checkpointing are low risk and can be on first. Compaction and tier fallback are next. The stuck-agent detector is last, because kill-and-respawn touches side effects; pair it with the idempotency check above. Keep `ATLAS_SELF_HEALING=0` as the kill switch.
