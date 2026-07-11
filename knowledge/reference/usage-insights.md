---
name: usage-insights
category: reference
description: Observed usage patterns and efficiency recommendations logged by atlas-ai-eng during high usage.
audience: [atlas-ai-eng, atlas-lead]
tags: [usage, patterns, efficiency, downgrades]
---

# Usage insights

atlas-ai-eng logs observed usage patterns and efficiency recommendations here, especially during high usage. The user approves changes through `ways-of-working.md`. No secrets or PII.

## Patterns
Format:
```
- <pattern observed>. (date: <when>, evidence: <runs or signals>)
```

## Recommendations
Format:
```
- [ ] <recommendation>. (rationale: <why>, expected saving: <what>, date: <when>)
```

## Estimation accuracy
Track predicted vs actual size to improve future estimates.
```
- run <id>: predicted <light|medium|heavy>, actual <...>, note <...>
```

## Model downgrades
Log automatic downgrades so premium-tier pressure is visible over time. See `model-resilience.md` for the policy.
```
- downgrade: <role> <from-tier> to <to-tier>, reason <quota|rate-limit|unavailable|blocked>, run <run-id>, date <when>
```

## OTel spans
Structured spans from trajectory.jsonl. Upgraded to OpenTelemetry GenAI semantic conventions in v0.13.0. See `observability-system.md` for the full span schema and 8 multi-agent metrics.

```
- traceId: <run-id>
  spanId: <span>
  parentSpanId: <parent>
  agent.name: <role>
  workflow.phase: <phase>
  workflow.variant: <small|full>
  outcome: <success|failure|escalated|skipped>
  error.category: <none|timeout|rate_limit|validation|delegation|context|resource>
  tokens.input/output/total: <n>
  duration.ms: <n>
```

## Anomaly detections
Patterns detected across runs. See `observability-system.md` for detection rules.
```
- anomaly: <repeater|wanderer|looper|budget_bleed|escalation_storm|gate_blockade>, role <role>, detected <date>, action <taken>
```

## Quality scores
Composite scores per run. See `decision-quality-scoring.md` for the 6 dimensions and weights.
```
- run <id>: roleAdherence <0-1>, gateEffectiveness <0-1>, handoffQuality <0-1>, delegationAccuracy <0-1>, escalationQuality <0-1>, planFidelity <0-1>, composite <0-1>
```

## Drift alerts
Auto-created when patterns degrade. Auto-expires after 30 days of no recurrence.
```
- drift: <role> <finding>, detected <date>, expires <date>, status <active|expired>
```
