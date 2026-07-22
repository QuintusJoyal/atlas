---
name: observability-system
category: process
status: experimental — opt-in, not part of always-on core
load-when: User explicitly asks for OTel-style tracing or dashboard mockups during the monthly self-assessment workflow
skip-when: Normal operation, simple tasks, everyday delegation
description: Illustrative OTel-shaped presentation of Atlas trajectory data. Spans, metrics, anomaly detection, dashboard concepts. No real tracing backend is included in this bundle.
audience: [atlas-lead, atlas-ent-arch, atlas-ai-eng]
tags: [observability, tracing, metrics, otel, anomaly-detection, dashboard, experimental]
---

# Observability system (experimental)

This bundle has no OTel collector, span exporter, or metrics store. What follows is a way to *format* trajectory-log data (see `knowledge/process/trajectory-logging.md`) as OTel-shaped spans and dashboard mockups for a human reader — useful for the monthly `workflows/self-assessment.md` narrative, not a real telemetry pipeline. The "metrics" below require inputs (expected tokens, serial-time-if-sequential) nobody measures; treat any number produced here as an illustrative estimate the agent states its assumptions for, never as a precise measurement.

## Quick Reference
- Trace = run-id, Span = individual decision/tool call
- 8 multi-agent metrics unique to Atlas
- 6 anomaly patterns with detection rules
- Dashboard: run overview, per-role drill-down, team coordination, anomaly panel

## OTel span hierarchy

```
Trace: run-id
  Span: create_agent (atlas-lead creates delegation)
  Span: invoke_agent_internal (role executes task)
    Span: execute_tool (tool call within role)
  Span: gate_check (critic evaluation)
  Span: divergence_check (parallel output comparison)
```

### Core attributes (gen_ai.*)

| Attribute | Description |
|-----------|-------------|
| `gen_ai.system` | "atlas" |
| `gen_ai.agent.name` | Role name (atlas-dev, atlas-qa, etc.) |
| `gen_ai.request.model` | Model used for this span |
| `gen_ai.response.token_count` | Tokens consumed |
| `gen_ai.agent.state` | active, completed, failed |

### Atlas-specific attributes (atlas.*)

| Attribute | Description |
|-----------|-------------|
| `atlas.role.tier` | premium, standard, fast |
| `atlas.workflow.phase` | requirements, design, implementation, etc. |
| `atlas.workflow.variant` | small, full |
| `atlas.handoff.quality` | Handoff quality score (0-1) |
| `atlas.gate.type` | requirements, design, final |
| `atlas.critic.id` | Critic name (for critic spans) |
| `atlas.critic.verdict` | pass, fail |
| `atlas.divergence.found` | true, false |

## 8 multi-agent metrics

These metrics are unique to multi-agent systems. No single-agent framework produces them.

### 1. IAHQS — Inter-Agent Handoff Quality Score
Measures whether handoffs contain everything the next role needs.
```
IAHQS = 1 - (rework_caused_by_incomplete_handoff / total_handoffs)
```
Target: > 0.90

### 2. DAS — Delegation Accuracy Score
Measures whether atlas-lead routes to the correct role.
```
DAS = correct_routes / total_routes
```
A route is "correct" if the delegated role completed without needing re-routing.

### 3. EJR — Escalation Justification Rate
Measures whether escalations are well-structured.
```
EJR = escalations_with_structured_payload / total_escalations
```
Structured payload = includes what was tried, what failed, what's needed.

### 4. GYR — Gate Yield Rate
Measures how often gates pass on first attempt.
```
GYR = gates_passed_first_attempt / total_gate_checks
```
Low GYR means pre-handoff quality checks are insufficient.

### 5. REI — Role Efficiency Index
Measures token efficiency per role relative to task complexity.
```
REI = expected_tokens / actual_tokens
```
REI > 1.0 means the role used fewer tokens than expected. < 1.0 means over-consumption.

### 6. CPS — Context Propagation Score
Measures whether context flows correctly through the pipeline.
```
CPS = 1 - (context_re_derivation_events / total_delegations)
```
Context re-derivation = when a role had to re-read or re-derive something the prior role should have passed.

### 7. PER — Parallel Efficiency Ratio
Measures how effectively parallel phases use concurrent execution.
```
PER = serial_time_if_sequential / actual_parallel_time
```
PER > 1.0 means parallelism saved time. PER = 1.0 means no benefit from parallelism.

### 8. MTAS — Model Tier Appropriateness Score
Measures whether the right tier was used for each role.
```
MTAS = 1 - (tier_mismatches / total_roles)
```
A tier mismatch = fast tier used for a premium-gate role, or premium used for a routine task.

## Anomaly detection patterns

Six patterns that indicate agent dysfunction:

### 1. Repeater
Same error 3+ times from same role.
- Detection: count outcome=failure entries with same error field per role
- Action: escalate to T3, inject corrective lesson into role brief

### 2. Wanderer
Topic drift — outputs diverge from original task.
- Detection: compare handoff summary against original task description using semantic similarity
- Action: pause role, re-anchor with original task + constraints

### 3. Looper
Cycle detected — same decision repeated.
- Detection: find identical "why" fields in trajectory entries from same role
- Action: escalate to T2 with loop context

### 4. Budget Bleed
Token consumption exceeds predicted by 2x.
- Detection: compare actualTokens against predicted in budget.md
- Action: pause, present to user for re-approval

### 5. Escalation Storm
3+ escalations in a single run.
- Detection: count outcome=escalated entries per run
- Action: pause all active roles, lead reassesses plan

### 6. Gate Blockade
Gate fails 3+ times (3-strike exhausted).
- Detection: count gate-check entries with outcome=failure for same gate
- Action: escalate to user with critic findings

## Dashboard concepts

### Run Overview
```
Phase Timeline: [requirements] → [design] → [implement] → [test] → [review] → [deploy]
                ✓ 1200 tok      ✓ 3500      ◐ 2100        ○ pending   ○ pending   ○ pending
Quality: Gate Yield 100% | Handoff Quality 0.92 | Divergence: 0 found
Reasoning/Action Ratio: 32% / 68% (healthy)
```

### Per-Role Drill-Down
```
atlas-dev (fast):
  Tokens: 14,400 (Read) + 3,200 (Edit) + 6,000 (Bash) = 23,600 total
  Quality: REI 1.12 | Handoff 0.95 | Escalations 0
  Trust Score: 0.87 (HIGH) | Trend: ↑ 0.03 vs last run
```

### Team Coordination
```
Handoff Matrix:
  atlas-pm → atlas-ba:      0.94 quality (3 handoffs)
  atlas-architect → atlas-dev: 0.88 quality (2 handoffs)
  atlas-dev → atlas-qa:     0.91 quality (2 handoffs)
Divergence Incidents: 0 this run | 2 this month
```

### Anomaly Panel
```
Active Alerts: none
Recent: Repeater detected in atlas-qa (oracle leakage, 3 runs in a row)
Drift Alerts: atlas-dev "avoid mock.verify" — auto-expires 2026-08-11
```
