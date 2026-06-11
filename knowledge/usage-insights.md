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

(empty)
