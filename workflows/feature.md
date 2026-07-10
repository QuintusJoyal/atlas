# Workflow: feature

Full pipeline for net-new work. All three approval gates plus token-budget kickoff.

## Phase 0: Kickoff (before requirements)
1. atlas-lead: pick this preset, tell the user **workflow + rationale**, create run folder, seed `team.json`.
2. Estimation huddle via **Task**: atlas-ai-eng aggregates; participating roles each return light | medium | heavy for their phase.
3. atlas-lead writes `budget.md` (use `budget-template.md`): **Predicted**, **Estimates by role**, workflow line.
4. **Gate: token-budget** (user approves if heavy; light/medium may proceed with acknowledgment).
5. Do **not** start requirements or build Tasks until kickoff artifacts exist.

## Phases and roles
1. Requirements: atlas-pm (with atlas-ba)
2. Analysis: atlas-ba
3. Gate 1: requirements (user)
4. Design: atlas-architect, atlas-ux (parallel)
5. Gate 2: design (user)
6. Implementation: atlas-dev (atlas-docs drafts in parallel)
7. Testing: atlas-qa
8. Review: atlas-reviewer
9. Security gate: atlas-security (atlas-compliance if regulated)
10. Gate 3: final delivery (user)
11. Deploy: atlas-devops
12. Maintenance handoff: atlas-maintenance

## Default tiers
Premium: atlas-architect, atlas-security, atlas-reviewer, atlas-lead. Standard: atlas-pm, atlas-ba, atlas-ux, atlas-qa, atlas-devops. Fast: atlas-dev, atlas-docs.

## Definition of Done per gate
- Requirements: testable acceptance criteria; scope clear; open questions closed or escalated.
- Design: NFRs stated; key decisions recorded as ADRs; trade-offs noted.
- Final delivery: tests pass; security and review clear or risks accepted; docs updated.
