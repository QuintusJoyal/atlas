---
name: performance-optimization
description: Profile, identify bottleneck, optimize, benchmark, verify no regression.
type: standard
triggers:
  - slow-endpoint
  - high-latency
  - performance-degradation
  - capacity-planning
variants:
  small:
    description: Quick optimization, clear bottleneck, low risk.
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Complex optimization, multiple bottlenecks, or performance-critical path.
    gates: [design, final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: technical-deep-dive
    add: [architecture-review]
    add-roles: [atlas-architect]
  - if: security-sensitive
    add: [security-review]
    add-roles: [atlas-security]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: performance optimization

Measure first. Optimize second. Verify third. Never optimize without data.

## Variant selection

Pick variant based on complexity:
- **small:** single endpoint, clear metric, known pattern (add index, cache, N+1 fix)
- **full:** system-wide performance, multiple bottlenecks, requires profiling and load testing

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, write budget.md
- **Lightweight:** create run folder, start immediately

## Phases

### profiling
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (standard), atlas-devops (standard for infrastructure metrics)
- **Input:** performance issue description, baseline metrics, affected endpoints
- **Output:** profiling-report.md (bottleneck identification, resource utilization, baseline measurements)

### optimization
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (standard)
- **Input:** profiling-report.md, affected code
- **Output:** implementation summary (changes made, expected improvement, risk assessment)

### benchmarking
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-qa (standard), atlas-dev (fast)
- **Input:** implementation summary, baseline measurements
- **Output:** benchmark-results.md (before/after comparison, statistical significance, regression check)

### review
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-reviewer (standard)
- **Input:** implementation diff, benchmark results
- **Output:** review.md (verdict, findings, performance impact confirmed)

## Definition of Done

- [ ] Baseline measurements documented before optimization
- [ ] Bottleneck identified with evidence (not guessed)
- [ ] Optimization shows measurable improvement (statistically significant)
- [ ] No regression in other areas (full test suite passes)
- [ ] Changes are maintainable (no clever hacks that nobody understands)
- [ ] User has signed off (full only; small auto-approves)
