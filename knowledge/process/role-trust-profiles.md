---
name: role-trust-profiles
category: process
status: experimental — opt-in, not part of always-on core
load-when: User explicitly asks for trust-based tier routing, or during the monthly self-assessment workflow
skip-when: Normal delegation, simple tasks, everyday routing
description: Adaptive role trust scoring (ARTS) — an illustrative model. Trust profiles track role performance and guide tier allocation. Requires the user to opt in; the formula's inputs are not measured by anything in this bundle by default.
audience: [atlas-lead, atlas-ent-arch]
tags: [trust, scoring, adaptive, tier, performance, ARTS, experimental]
---

# Role trust profiles (ARTS) (experimental)

Adaptive Role Trust Scoring tracks how well each role performs and uses that data to guide model tier allocation. Roles that consistently perform well get faster/cheaper tiers. Roles that struggle get premium tiers.

This is opt-in, not part of the always-on core: the score formula below needs inputs (quality averages, critic pass rates) that only exist if the user has also opted into `decision-quality-scoring.md` and is running enough repeat work for the numbers to mean anything. Without that, treat any score here as the agent's honest self-estimate, stated with its reasoning, not a measured quantity.

## Quick Reference
- Trust score per role: 0.0 (untrusted) to 1.0 (fully trusted)
- 4 tiers: UNTRUSTED (0.0-0.3), PROBATION (0.3-0.6), STANDARD (0.6-0.8), TRUSTED (0.8-1.0)
- Tier allocation: trust score determines which model tier a role gets
- Decay: trust scores decay if a role hasn't been used recently
- Stored in `ATLAS_DATA_DIR/trust-profiles.json`

## Trust score calculation

### Inputs
1. **Quality scores** from `decision-quality-scoring.md` (weighted average of 6 dimensions)
2. **Critic pass rate** — percentage of critic evaluations that pass
3. **Rework rate** — percentage of tasks requiring re-work
4. **Escalation rate** — percentage of tasks escalated to higher tiers
5. **Task complexity** — adjusted for task difficulty

### Formula
```
trust_score = (quality_avg * 0.40) +
              (critic_pass_rate * 0.30) +
              (1 - rework_rate * 0.20) +
              (1 - escalation_rate * 0.10)
```

### Score decay
If a role hasn't been used in 30+ days:
```
decay = 0.95 ^ (days_since_last_use / 30)
trust_score = trust_score * decay
```

## Trust tiers

| Tier | Score Range | Model Allocation | When Used |
|------|-------------|-----------------|-----------|
| UNTRUSTED | 0.0 - 0.3 | Premium (always) | New role, poor performance |
| PROBATION | 0.3 - 0.6 | Premium (prefer) | Recovering from failure |
| STANDARD | 0.6 - 0.8 | Standard (default) | Normal operation |
| TRUSTED | 0.8 - 1.0 | Fast (prefer) | Consistent high performance |

## Trust profile structure

```json
{
  "atlas-dev": {
    "trustScore": 0.87,
    "tier": "TRUSTED",
    "qualityAvg": 0.91,
    "criticPassRate": 0.88,
    "reworkRate": 0.05,
    "escalationRate": 0.02,
    "taskCount": 47,
    "lastUsed": "2026-07-11",
    "lastQualityScore": 0.92,
    "driftAlerts": 0,
    "trend": "stable"
  },
  "atlas-qa": {
    "trustScore": 0.62,
    "tier": "STANDARD",
    "qualityAvg": 0.75,
    "criticPassRate": 0.70,
    "reworkRate": 0.15,
    "escalationRate": 0.10,
    "taskCount": 32,
    "lastUsed": "2026-07-10",
    "lastQualityScore": 0.78,
    "driftAlerts": 1,
    "trend": "improving"
  }
}
```

## Tier allocation rules

### Default allocation
- Atlas-lead checks trust profile before each delegation
- Role gets model tier based on trust tier
- UNTRUSTED → premium, PROBATION → premium (prefer), STANDARD → standard, TRUSTED → fast

### Override: task complexity
- Complex tasks override trust-based allocation
- Even TRUSTED roles get premium for critical-path tasks
- Atlas-lead documents override reason in team.json

### Override: user request
- User can force premium for any role
- User can force fast for any role
- Overrides are logged in budget.md

## Trust updates

After each task completion:
1. Quality score is calculated (from `decision-quality-scoring.md`)
2. Trust score is updated using the formula
3. Trust tier is recalculated
4. If tier changed, log the change in `usage-insights.md`

```
Trust update: atlas-dev: 0.85 → 0.87 (TRUSTED, trend: stable)
Trust update: atlas-qa: 0.58 → 0.62 (PROBATION → STANDARD, trend: improving)
```

## Integration with routing

Atlas-lead uses trust profiles for:
1. **Model tier selection** — trust-based allocation
2. **Delegation priority** — higher trust roles get critical-path tasks first
3. **Parallel assignment** — TRUSTED roles can handle parallel tasks safely
4. **Risk assessment** — UNTRUSTED roles on critical path = higher risk

## Trust resets

Trust scores reset when:
- User explicitly resets a role's trust
- Role definition changes significantly (new agent file)
- Role has been inactive for 90+ days (full decay)
