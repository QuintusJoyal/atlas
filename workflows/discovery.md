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
    skip: [research]
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

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
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

## Lite mode

Generated into `lite/workflows/discovery.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# Discovery (Lite)

## Phase 1: Research
- **Roles:** atlas-pm + atlas-ba
- **Input:** user question or problem statement
- **Output:** problem framing, success criteria
- **Gate:** problem framed, success criteria set

## Phase 2: Feasibility
- **Roles:** atlas-architect (+ atlas-cloud if cloud-relevant)
- **Input:** problem framing
- **Output:** approach options with trade-offs
- **Gate:** approach chosen, trade-offs named

## Phase 3: Recommendation
- **Roles:** atlas-pm
- **Input:** feasibility analysis
- **Output:** go/no-go recommendation with next steps
- **Gate:** user decides go/no-go

## Definition of Done
- [ ] Problem clearly framed
- [ ] At least 2 approaches evaluated
- [ ] Recommendation with trade-offs
- [ ] User decides go/no-go
<!-- lite:end -->
