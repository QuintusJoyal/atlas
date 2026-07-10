---
name: dora-metrics
load-when: Measuring delivery performance, benchmarking team productivity, identifying bottlenecks
skip-when: Incident management (see google-sre-practices), deployment practices (see gitops-principles)
---

# DORA Metrics

## Quick Reference
- Four key metrics: Deployment Frequency, Lead Time, Change Failure Rate, Time to Restore
- Elite performers: deploy on demand, lead time <1 hour, CFR <5%, TTR <1 hour
- Use metrics to improve, not to punish
- Metrics reflect system health, not individual performance

## Deep Dive

### Four Key Metrics
| Metric | What It Measures | Elite | High | Medium | Low |
|--------|-----------------|-------|------|--------|-----|
| Deployment Frequency | How often you deploy | On demand | Weekly to monthly | Monthly to 6 months | >6 months |
| Lead Time for Changes | Commit to deploy | <1 hour | 1 day to 1 week | 1 week to 1 month | >6 months |
| Change Failure Rate | % of deployments causing failure | 0-15% | 16-30% | 16-30% | >30% |
| Time to Restore Service | Mean time to recover | <1 hour | <1 day | <1 day | >1 week |

### DORA Capabilities
- **Lean management**: visual management, limit WIP, manage flow
- **Continuous delivery**: trunk-based development, CI/CD, deployment automation
- **Lean product development**: customer research, MVP, fast feedback
- **Organizational learning**: blameless culture, time to learn, local experimentation

### Using DORA Metrics
1. Measure current state (baseline)
2. Identify bottleneck metric (lowest performing)
3. Set improvement target
4. Implement changes
5. Re-measure after 2-3 months
6. Repeat

### Common Patterns
- **High deployment frequency + high CFR**: deploying fast but breaking things
- **Low deployment frequency + low CFR**: afraid to deploy, over-testing
- **Long lead time**: bottleneck in CI/CD or review process
- **Long TTR**: poor observability or incident response

### Anti-Gaming
- Don't cherry-pick easy deployments to boost frequency
- Don't batch changes to reduce CFR
- Don't count only "successful" deployments
- Measure at the system level, not per-developer

## See Also
- **google-sre-practices** — SLO/SLI/error budgets
- **gitops-principles** — Deployment and reconciliation
- **quality-gates** — Automated quality checks in CI/CD
- **anti-patterns** — Deployment and operational failures
