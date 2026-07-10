# Retro: <run-id>

Run: <run-id>
Workflow: <feature|bugfix|hotfix|...>
Date: <YYYY-MM-DD>
Participants: <roles and human>

Short outcome statement in one or two sentences. What shipped, paused, or failed.

## Went well

What worked. Be specific: artifacts, gates, delegations, tooling.

-
-

## Improve

What slowed the team, caused rework, or left gaps. No blame; focus on system and process.

-
-

## Actions

Concrete follow-ups with owner and target date. Promote durable lessons to `proposed.md`; process changes to `ways-of-working.md`.

| Action | Owner | Due | Status |
| --- | --- | --- | --- |
| | | | open |

## Token efficiency

Structured FinOps slice for atlas-ai-eng and the next kickoff envelope.

### Wins

What saved tokens or model tier without hurting quality (parallel Tasks, reuse of artifacts, right tier on role, skipped regeneration).

-
-

### Waste

Where tokens went unnecessarily (lead monologue, duplicate specs, premium on low-risk work, failed Task retries without brief fix, context bloat).

-
-

### Next-run cuts

Specific changes for the next run's `budget.md` Predicted line and estimation huddle (smaller scope, fewer parallel premium roles, lighter workflow preset, playbook loads only when needed).

-
-

## Downgrades (if any)

Copy or summarize from `budget.md` Downgrades section. Flag premium gate roles that ran downgraded per `model-resilience.md`.

```
- downgrade: <role> <from> to <to>, reason <...>, date <...>
```

## Gate and quality summary

| Gate | Status | Notes |
| --- | --- | --- |
| Token budget | | |
| Requirements | | |
| Design | | |
| Final delivery | | |

Security / reviewer / compliance: clear | downgraded | risk accepted | not applicable

## Artifacts

| Artifact | Path | Notes |
| --- | --- | --- |
| | `$ATLAS_DATA_DIR/runs/<run-id>/...` | |

---

Template: copy to `$ATLAS_DATA_DIR/runs/<run-id>/retro.md` at end of run or after final gate. **Actual** usage in `budget.md` remains self-reported in v1; use this section until telemetry v2 (`core-values-charter.md`).
