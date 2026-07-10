---
name: discovery
description: Consulting mode. Produce scope and a proposal. No build.
type: assessment
triggers:
  - research
  - technical-exploration
  - proof-of-concept
variants:
  small:
    description: Quick feasibility check. Single gate.
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Full discovery with proposal and SOW outline.
    gates: [research, final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: technical-deep-dive
    add-roles: [atlas-architect]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: discovery

Consulting mode. Produce scope and a proposal. No build.

## Variant selection

Pick variant based on depth needed:
- **small:** quick feasibility check, yes/no answer, rough estimate
- **full:** problem framing, options analysis, proposal with SOW outline

Tell the user which variant you picked and why.

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### research
- **Gate:** research (full only)
- **Parallel:** true
- **Roles:** atlas-consultant (standard), atlas-pm (standard), atlas-ba (fast)
- **Skip-if:** variant=small
- **Input:** user goal, problem statement
- **Output:** research summary (current state, constraints, options)

### feasibility
- **Gate:** null
- **Parallel:** true
- **Roles:** atlas-architect (premium) or atlas-ent-arch (premium), atlas-cloud (premium if cost relevant)
- **Input:** research summary
- **Output:** feasibility assessment (approach, cost estimate, risks)

### proposal
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-consultant (standard)
- **Input:** research summary, feasibility assessment
- **Output:** proposal (scope, options, trade-offs, SOW outline)

## Definition of Done (auto-approve if small)

- [ ] Problem framed (MECE); current and desired state captured
- [ ] Options with trade-offs and rough cost
- [ ] Proposal or SOW outline ready for the user
- [ ] No build started
- [ ] User has signed off (full only; small auto-approves if all above pass)
