---
name: atlas-framework
category: reference
description: Explanation of where Atlas sits among agentic SDLC frameworks, runtime architecture, and operator usage guide.
audience: [atlas-lead, atlas-dev, atlas-architect]
tags: [framework, architecture, operator-guide, runtime]
---

# Atlas framework

Explanation of where Atlas sits among agentic SDLC frameworks, how the runtime works, and how operators use the bundle day to day.

## What Atlas is

Atlas is a **self-contained IDE subagent bundle**: 24 specialist roles, workflow presets, approval gates, and shared knowledge base. Execution stays in your IDE; governance and visibility live in chat plus run artifacts under `$ATLAS_DATA_DIR/runs/<run-id>/`. Project repos do not hold Atlas state. An optional SDK orchestrator ships with Control Center, not this bundle.

Tagline: *One team. Every discipline. Under your command.*

## Comparison with other AI frameworks

High-level positioning. Each project evolves quickly; verify current docs before adopting.

| Framework | Primary shape | Strengths | Gaps vs Atlas |
| --- | --- | --- | --- |
| **BMAD** (Breakthrough Method for Agile AI-Driven Development) | Agent personas + agile ceremonies in chat | Strong product and scrum framing; story-driven flow | No bundled enterprise roles, token FinOps, or gate sidecars |
| **GSD** (Get Shit Done) | Task lists and execution loops in IDE | Fast iteration; minimal ceremony | Light governance; no multi-gate enterprise model or specialist roster |
| **Hermes** | Multi-agent orchestration runtime | Agent routing and tool use at scale | External runtime; Atlas stays IDE-native with optional SDK |
| **MetaGPT** | Role-based company simulation (PM, architect, engineer) | Clear role split; familiar SOP pattern | Python-centric; less IDE-integrated; Atlas maps roles to IDE subagents + disk artifacts |
| **Spec Kit** (GitHub) | Spec-driven: constitution, specify, plan, tasks | Excellent spec and plan artifacts in repo | No 24-role enterprise map or token budget protocol |

**Atlas hybrid**: BMAD-style roles and gates + Spec Kit-style repo artifacts + Hermes-style delegation. MetaGPT-like role clarity without replacing the IDE as the executor.

## Runtime architecture

```
User
  │
  ├─ IDE chat (/atlas-lead, /atlas-<role>)
  │     └─ Delegation → subagents (separate model allocation)
  │
  └─ Central data home: $ATLAS_DATA_DIR/runs/<run-id>/
        artifacts, team.json, gates/, budget.md
```

| Layer | Responsibility |
| --- | --- |
| **IDE Delegation** | Specialist work at assigned model tier; re-delegate on quota per `model-resilience.md` |
| **atlas-lead** | Orchestration only: kickoff, briefs, `team.json`, gate sequencing, summaries |
| **Run workspace** | Source of truth under `$ATLAS_DATA_DIR/runs/<run-id>/`; not in project repos |
| **Signal Deck + SDK** ([`atlas-control-center`](https://github.com/QuintusJoyal/atlas-control-center), `./sdk/`) | Optional operator UI and headless pipeline runner; not installed by the bundle |

Install copies bundle to your IDE config directory and knowledge to `$ATLAS_DATA_DIR/knowledge/`. Repo `knowledge/` is the ship source; after install, roles read the installed copy.

## Operator guide

### Prerequisites

1. Atlas bundle installed (`install.ps1` or `install.sh`).
2. Fresh orchestrator chat after install or bundle update (see below).

### Fresh atlas-lead chat after install

After install or update:

1. Open a **new** IDE chat (do not continue a pre-install thread).
2. Run `/atlas-lead help` to confirm agents and rules loaded.
3. Start pipeline work from that chat so kickoff, delegations, and summaries use current rules.

Stale chats may miss new orchestration rules (delegation-only lead, kickoff mandatory, model resilience).

### Dogfood acceptance checklist (6 steps)

Use this to accept a real Atlas run on a small feature.

| Step | Action | Pass criteria |
| --- | --- | --- |
| 1 | New `/atlas-lead` chat; kick off a small feature run | Run folder created; `team.json` and `budget.md` present |
| 2 | Complete kickoff | Workflow announced; role estimates in `budget.md` |
| 3 | Requirements phase via delegation | `requirements.md` exists; gate 1 pending user approval |
| 4 | Approve requirements in chat | `gates/requirements.json` status `approved` |
| 5 | Design + build phases | Artifacts on disk; `team.json` shows delegation progress |
| 6 | Final gate | User sign-off; retro notes optional |

Optional: from the Control Center repo, `docker compose run --rm sdk-runner npm run pipeline -- "<task>"` surfaces gate prompts in the console (see `sdk/README.md` in [`atlas-control-center`](https://github.com/QuintusJoyal/atlas-control-center)).

### Legacy run warn-only behavior

Runs created before framework v1 lack `frameworkVersion: 1` in `team.json`.

| Behavior | Legacy run | v1 run (`frameworkVersion: 1`) |
| --- | --- | --- |
| Kickoff fields | Lead should still complete kickoff; warn if gaps | Full kickoff checklist enforced in playbook |
| Upgrade path | Add `frameworkVersion: 1` to `team.json` and complete kickoff fields | Full validator expectations in charter docs |

New runs should set `frameworkVersion: 1` at kickoff.

### Day-to-day visibility

| Artifact | Use for |
| --- | --- |
| `team.json` | Who owns what, delegation status, model tier notes |
| `gates/*.json` | Gate approval state (requirements, design, final, token-budget) |
| `budget.md` | Predicted usage, role estimates, downgrade log |
| Run markdown | Requirements, design, tests, review, security |

Inspect `$ATLAS_DATA_DIR/runs/<run-id>/` directly or ask atlas-lead for a roster summary in chat.

## Workflow presets

| Preset | Gates | When |
| --- | --- | --- |
| feature | Requirements, design, final (+ token-budget if heavy) | Net-new work |
| bugfix / hotfix | Final | Defects; hotfix expedited deploy |
| data-project | All three | Pipelines, analytics, ML |
| infra-change | Design + final (+ security) | Cloud, network, CI/CD |
| security-audit | Final (findings) | Audit only |
| discovery | Requirements | Scope and proposal |

See `workflows/*.md` and `skills/atlas-lead-playbook/SKILL.md`.

## References

- `README.md`, `ROLES.md`
- `knowledge/model-resilience.md`
- `knowledge/budget-template.md`
- [`atlas-control-center/sdk/README.md`](https://github.com/QuintusJoyal/atlas-control-center/blob/main/sdk/README.md)
