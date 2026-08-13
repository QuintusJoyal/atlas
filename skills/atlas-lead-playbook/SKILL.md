---
name: atlas-lead-playbook
description: Orchestration playbook for atlas-lead.
type: playbook
appliesTo: [atlas-lead]
tags: [playbook, orchestration]
---

# atlas-lead

## Route
- new feature, enhancement → lead (orchestrates full pipeline)
- bug, defect → lead (orchestrates bugfix pipeline)
- infrastructure change → lead (orchestrates infra pipeline)
- security concern → lead (orchestrates security pipeline)
- ambiguous request → lead (orchestrates discovery pipeline)

## Workflow

All 14 presets, gates as declared in each workflow file's own frontmatter (full variant — small is always final-only, except `documentation` small which has no gate at all). This table must match the workflow files; if they ever disagree, the workflow file wins.

| Preset | When | Gates (full) |
|--------|------|-------|
| feature | Net-new work | Requirements, design, final |
| bugfix | Defects, fast lane | Final only |
| data-project | Pipelines, analytics, ML | Requirements, design, final |
| infra-change | Infra, network, cloud changes | Requirements, design, final |
| security-audit | Read-only assessment, no code changes | Scope, final |
| discovery | Scope and proposal, no build | Research, final |
| api-design | API-first design with OpenAPI | Design, final |
| database-migration | Schema migration, staged rollout | Design, final |
| disaster-recovery | DR plan, failover testing, drills | Design, final |
| documentation | Docs-only changes | Final only |
| observability-setup | SLOs, dashboards, alerts | Design, final |
| performance-optimization | Profile, optimize, benchmark | Design, final |
| refactoring | Systematic code improvement | Design, final |
| self-assessment | Monthly Atlas capability review | Final only |

Unknown task shapes fall back to `feature`, but check this table first — most task shapes have a closer-fitting preset than feature.

## Knowledge
- Scrum Guide → k/scrum-guide
- RAID tracking → k/raid-log-management
- RACI assignment → k/raci-matrix
- Conflict resolution → k/mece-framework

## Scope
orchestration, workflow selection, delegation, gate management, team manifest, token budget, status reporting | NOT implementation (→ dev), testing (→ qa), design (→ architect), security (→ security), requirements (→ pm/ba)

## Delegation Examples
### Feature pipeline
"New CSV export feature." → pm (stories) → **requirements gate** → architect + ux (design, parallel) → **design gate** → dev (implement) → qa (test) → security + reviewer (parallel) → **final gate** → deploy. Requirements and design are sequential, not parallel — design needs the approved requirements.md as input.

### Bug investigation
"Users reporting 500 errors on checkout." → qa (investigate + reproduce) + dev (fix) in parallel → qa (verify fix) → deploy.

### Ambiguous request
"Users are confused by the dashboard." → pm (clarify problem, interview user) → ba (edge cases) → architect + ux (design) → dev → qa.

## Lite mode

Generated into `lite/skills/atlas-lead-playbook/SKILL.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# atlas-lead (Lite Playbook)

## Workflow Selection
- "add feature" / "build" → feature workflow
- "fix bug" / "broken" / "error" → bugfix workflow
- "research" / "explore" / "investigate" → discovery workflow

## Rules
1. Read state.md first. Know where you are in the pipeline.
2. Delegate one role at a time. Brief: Goal + Context + Files.
3. After handoff: read it, update state.md, delegate Next.
4. Tell the user after each phase completes.
5. If stuck or uncertain, stop and ask the user.
<!-- lite:end -->
