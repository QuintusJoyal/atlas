---
name: dashboard-spec
category: process
status: experimental — opt-in, not part of always-on core
load-when: User explicitly asks for a dashboard-style summary during the monthly self-assessment workflow
skip-when: Normal operation, everyday delegation
description: Illustrative dashboard layout for presenting Atlas's experimental telemetry (trust profiles, decision-quality scores). No IDE actually renders this natively — it's a format for the agent to fill in by hand when asked.
audience: [atlas-lead, atlas-ent-arch, atlas-ai-eng]
tags: [dashboard, observability, metrics, visualization, monitoring, experimental]
---

# Dashboard specification (experimental)

This is a layout spec, not a working dashboard. Every number in the panels below (trust scores, quality scores, gate yield, divergence counts) comes from the experimental, opt-in files this depends on (`observability-system.md`, `role-trust-profiles.md`, `decision-quality-scoring.md`) — treat them as the agent's illustrative self-assessment, not measured data, per those files' own caveats. No IDE (Cursor, Claude Code, OpenCode, or otherwise) renders this automatically; "Implementation notes" below describes how a human could format the same data by hand in each IDE's UI, not a feature that exists today.

## Quick Reference
- 4 panels: Run Overview, Per-Role, Team Coordination, Anomaly Panel
- Data sources: trajectory.jsonl, trust-profiles.json, usage-insights.md
- Update frequency: real-time during runs, daily summary
- Format: specification with mock layouts and data schemas

## Panel 1: Run Overview

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Run: run-20260711-central-data-home                         │
│ Workflow: feature (full) | Status: in_progress              │
├─────────────────────────────────────────────────────────────┤
│ Phase Timeline                                              │
│ [requirements] → [design] → [implement] → [test] → [review]│
│   ✓ 1,200 tok    ✓ 3,500    ◐ 2,100      ○      ○         │
├─────────────────────────────────────────────────────────────┤
│ Quality: Gate Yield 100% | Handoff Quality 0.92             │
│ Budget: 6,800 / 10,000 tokens (68%)                        │
│ Duration: 12m 34s | Phases: 2/5 complete                   │
└─────────────────────────────────────────────────────────────┘
```

### Data schema
```json
{
  "runId": "run-20260711-central-data-home",
  "workflow": "feature",
  "variant": "full",
  "status": "in_progress",
  "phases": [
    {"name": "requirements", "status": "completed", "tokens": 1200, "duration_ms": 45000},
    {"name": "design", "status": "completed", "tokens": 3500, "duration_ms": 120000},
    {"name": "implementation", "status": "active", "tokens": 2100, "duration_ms": 90000}
  ],
  "quality": {"gateYield": 1.0, "handoffQuality": 0.92},
  "budget": {"predicted": 10000, "actual": 6800, "remaining": 3200},
  "duration_ms": 754000
}
```

## Panel 2: Per-Role Performance

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Role Performance                                            │
├─────────────┬──────────┬──────────┬──────────┬─────────────┤
│ Role        │ Trust    │ Quality  │ Tokens   │ Trend       │
├─────────────┼──────────┼──────────┼──────────┼─────────────┤
│ atlas-dev   │ 0.87     │ 0.92     │ 14,400   │ ↑ stable    │
│ atlas-qa    │ 0.62     │ 0.78     │ 8,200    │ ↑ improving │
│ atlas-arch  │ 0.91     │ 0.95     │ 6,500    │ → stable    │
│ atlas-pm    │ 0.85     │ 0.88     │ 3,200    │ → stable    │
├─────────────┴──────────┴──────────┴──────────┴─────────────┤
│ Trust Distribution: TRUSTED(3) STANDARD(1) PROBATION(0)    │
└─────────────────────────────────────────────────────────────┘
```

### Data source
- `trust-profiles.json` for trust scores and trends
- `trajectory.jsonl` for token usage per role
- `decision-quality-scoring.md` for quality scores

## Panel 3: Team Coordination

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Team Coordination                                           │
├─────────────────────────────────────────────────────────────┤
│ Handoff Matrix (quality scores)                             │
│ pm → architect:     0.94  architect → dev: 0.88            │
│ dev → qa:           0.91  qa → reviewer:  0.95             │
├─────────────────────────────────────────────────────────────┤
│ Parallel Efficiency: 1.2x (saved 300 tokens via parallel)  │
│ Divergence Incidents: 0 this run | 2 this month            │
│ Critics: 3 pass | 0 fail | 2 pending (gapped)              │
└─────────────────────────────────────────────────────────────┘
```

### Data source
- `trajectory.jsonl` for handoff events
- `divergence-detection.md` for divergence incidents
- `adversarial-critics.md` for critic verdicts

## Panel 4: Anomaly Panel

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Anomalies & Alerts                                          │
├─────────────────────────────────────────────────────────────┤
│ Active Alerts: none                                         │
├─────────────────────────────────────────────────────────────┤
│ Recent:                                                     │
│ - Repeater: atlas-qa oracle leakage (3 runs) [RESOLVED]   │
│ - Budget Bleed: atlas-dev exceeded 2x estimate [RESOLVED]  │
├─────────────────────────────────────────────────────────────┤
│ Drift Alerts:                                               │
│ - atlas-dev "avoid mock.verify" — expires 2026-08-11       │
│ - atlas-qa "test observable output" — expires 2026-08-11   │
└─────────────────────────────────────────────────────────────┘
```

### Data source
- `trajectory.jsonl` for anomaly events
- `lessons.md` for drift alerts
- `usage-insights.md` for pattern history

## Update frequency

| Panel | During Run | After Run | Daily |
|-------|-----------|-----------|-------|
| Run Overview | Real-time | Final | Summary |
| Per-Role | After each delegation | Final | Trend |
| Team Coordination | After each handoff | Final | Trend |
| Anomaly Panel | Real-time | Final | Cleanup |

## Data flow

```
trajectory.jsonl ──→ Panel 1 (Run Overview)
                  ──→ Panel 3 (Team Coordination)
                  ──→ Panel 4 (Anomaly Panel)

trust-profiles.json ──→ Panel 2 (Per-Role)

usage-insights.md ──→ Panel 2 (Per-Role trends)
                    ──→ Panel 4 (Anomaly history)

lessons.md ──→ Panel 4 (Drift alerts)
```

## Implementation notes

None of this is built. If a user asks for this view, the agent formats the same data by hand as plain markdown (tables, not charts) — there's no webview, terminal UI, or status-bar integration behind any IDE name below; these are just reasonable places a human might paste the output, not existing renderers:
- Cursor: as a markdown reply, or pasted into a scratch file
- OpenCode: as a markdown reply
- Claude Code: as a markdown reply, or appended to `CLAUDE.md` if the user wants it persisted
- VS Code Copilot: as a markdown reply

The data schema stays the same regardless of where the user pastes it.
