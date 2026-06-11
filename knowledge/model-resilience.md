# Model resilience and automatic downgrade

Canonical reference for keeping the workflow running when a model is quota-limited or unavailable. The user wants no interruptions for this. Roles and atlas-lead downgrade automatically, continue, log, and inform. They do not stop to ask.

## Tier cascade

Retry the affected step at the next tier down, in order:

| From | To |
| --- | --- |
| claude-opus-4-8-thinking-high | composer-2.5 |
| composer-2.5 | composer-2.5-fast |
| composer-2.5-fast | inherit |
| inherit | (exhausted: address the user) |

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

## Logging format

Record each downgrade in the run `budget.md` and append to `usage-insights.md`:

```
- downgrade: <role> <from-tier> to <to-tier>, reason <quota|rate-limit|unavailable|blocked>, run <run-id>, date <when>
```

## Quality flag

If a premium gate role (atlas-security, atlas-reviewer, atlas-architect) ran downgraded, flag it in the handoff and final summary so the user can re-run that gate at full tier if they want. The flag is informational and does not block delivery.
