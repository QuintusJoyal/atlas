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
- Conflict resolution → k/decision-frameworks

## Scope
orchestration, workflow selection, delegation, gate management, team manifest, token budget, status reporting | NOT implementation (→ dev), testing (→ qa), design (→ architect), security (→ security), requirements (→ pm/ba)

## Delegation Examples
### Feature pipeline
"New CSV export feature." → pm (stories) + architect (design) in parallel → dev (implement) → qa (test) → security + reviewer (gates) → deploy.

### Bug investigation
"Users reporting 500 errors on checkout." → qa (investigate + reproduce) + dev (fix) in parallel → qa (verify fix) → deploy.

### Ambiguous request
"Users are confused by the dashboard." → pm (clarify problem, interview user) → ba (edge cases) → architect + ux (design) → dev → qa.
