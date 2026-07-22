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
| Preset | When | Gates |
|--------|------|-------|
| feature | Net-new work | Requirements, design, final |
| bugfix | Defects | Final only |
| data-project | Pipelines, analytics, ML | All three |
| infra-change | CI/CD, cloud, network | Design + final |
| security-audit | Audit only | Final |
| discovery | Scope and proposal | Requirements only |

## Knowledge
- Scrum Guide → k/scrum-guide
- RAID tracking → k/raid-log-management
- RACI assignment → k/raci-matrix
- Conflict resolution → k/mece-framework

## Scope
orchestration, workflow selection, delegation, gate management, team manifest, token budget, status reporting | NOT implementation (→ dev), testing (→ qa), design (→ architect), security (→ security), requirements (→ pm/ba)

## Delegation Examples
### Feature pipeline
"New CSV export feature." → pm (stories) + architect (design) in parallel → dev (implement) → qa (test) → security + reviewer (gates) → deploy.

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
