---
name: lessons
category: reference
description: Canonical approved lessons the whole team follows — read before acting on any topic.
audience: [atlas-lead, all]
tags: [lessons, conventions, orchestration, data-home]
---

# Lessons (canonical)

Approved, durable lessons the whole team follows. Read the relevant topic before acting. Keep entries short. No secrets or PII.

Format:
```
## <topic>
- <lesson>. (source: <where it came from>, approved: <date>)
```

## Conventions
- Output uses the human-authored voice. No em dashes. (source: team charter, approved: 2026-06-11)
- Load rules and playbooks only when their topic is in motion. (source: team charter, approved: 2026-06-11)

## Approvals
- MCP write actions and the requirements, design, and final gates need user sign-off. (source: team charter, approved: 2026-06-11)

## Orchestration
- atlas-lead delegates every phase to the named role and never impersonates a role by writing its output in its own voice. If delegation is unavailable, raise it with the user rather than doing all the work in one thread. (source: user direction, approved: 2026-06-11)
- **Hard rule:** atlas-lead is orchestrator-only. All specialist deliverables (requirements, design, code, tests, security, review, docs) require delegation to the owning role. Quota failures trigger tier downgrade and re-delegation, not lead self-work. Explicit user waiver required to break this rule per task. (source: user direction, approved: 2026-06-12)
- Every run keeps `team.json` with role, phase, artifact, and delegation status. Inspect the run folder or ask lead for a roster summary. atlas-lead updates the manifest before and after each delegation. (source: user direction, approved: 2026-06-12)
- On usage limits, the **team continues**: atlas-lead downgrades one tier and **re-delegates to the same role** with the same brief. Lead never absorbs specialist work. Record `model`, `downgradedFrom`, and a note on the delegation row. (source: user direction, approved: 2026-06-12)
- **Never absorb on interrupt:** when delegation fails or hits quota, lead's only next action is delegation (same role, lower tier). Forbidden: editing code or artifacts inline, "I'll take over", marking role completed without delegation success. Token-budget pause does not authorize lead self-work. (source: user feedback, approved: 2026-06-12)
- **Lead self-limit:** when **atlas-lead's own session** hits quota, lead still delegates to specialist roles (separate allocation). Forbidden: lead implements inline because "I'm at limit." Lead default tier is standard, not premium. (source: user feedback, approved: 2026-06-12)
- **Kickoff is mandatory:** every pipeline announces workflow + rationale, runs estimation huddle (roles return light/medium/heavy; atlas-ai-eng aggregates), writes `budget.md` and `team.json.budget` before the first specialist delegation. (source: user feedback, approved: 2026-06-12)
- **Delegation invoke cascade:** on delegation launch failure, atlas-lead re-triggers in the same turn, stepping through the model cascade before stopping; map frontmatter slugs to valid models per `model-resilience.md`. (source: run 2026-06-14-central-data-home, approved: 2026-06-17)

## Data home
- Atlas global state (runs, tickets, config, jobs, activity) lives under `ATLAS_DATA_DIR` (default `$ATLAS_DATA_DIR`), not repo `.atlas/`; `meta.workspace` ties each run to a code checkout. (source: run 2026-06-14-central-data-home design.md, approved: 2026-06-17)
