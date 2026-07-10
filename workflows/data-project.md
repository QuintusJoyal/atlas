---
name: data-project
description: Data or analytics work. Pulls the data roles into the chain.
type: pipeline
triggers:
  - data-work
  - analytics
  - reporting
variants:
  small:
    description: Small data task, single gate. Skip requirements/design gates.
    gates: [final]
    skip: [requirements-gate, design-gate, design]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Full data pipeline with all gates.
    gates: [requirements, design, final]
    token-estimate: medium-heavy
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: security-sensitive
    add: [security-review]
    add-roles: [atlas-security]
  - if: regulated
    add: [compliance]
    add-roles: [atlas-compliance]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: data-project

Data or analytics work. Pulls the data roles into the chain.

## Variant selection

Pick variant based on scope:
- **small:** ad-hoc query, simple report, data quality check, <1 data source
- **full:** new pipeline, ML model, data warehouse, multiple data sources, regulated data

Tell the user which variant you picked and why.

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### requirements
- **Gate:** requirements
- **Parallel:** false
- **Roles:** atlas-pm (standard), atlas-ba (fast)
- **Skip-if:** variant=small
- **Input:** user goal or data request
- **Output:** requirements.md (data sources, grain, metric definitions, acceptance criteria)

### design
- **Gate:** design
- **Parallel:** true
- **Roles:** atlas-data-eng (standard), atlas-dba (standard), atlas-data-sci (standard if ML), atlas-architect (premium)
- **Skip-if:** variant=small
- **Input:** requirements.md
- **Output:** design.md (pipeline DAG, data model, quality checks, lineage)

### build
- **Gate:** null
- **Parallel:** true
- **Roles:** atlas-data-eng (standard), atlas-data-sci (standard if ML)
- **Input:** design.md, source schemas
- **Output:** implementation summary (pipeline code, model code, data contracts)

### validate
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-data-analyst (fast), atlas-qa (standard)
- **Input:** implementation summary, requirements.md
- **Output:** validation results (data quality checks, metric validation, analysis)

### review
- **Gate:** final
- **Parallel:** true
- **Roles:** atlas-reviewer (premium), atlas-security (premium if sensitive data), atlas-compliance (premium if regulated)
- **Input:** implementation diff, validation results, security findings
- **Output:** review.md (verdict, findings)

### deploy
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard)
- **Input:** merge approval, security clearance
- **Output:** deployment artifact (pipeline config, monitoring, alerts)

## Definition of Done per gate

### Requirements gate (full only)
- [ ] Data sources, grain, and metric definitions agreed
- [ ] Acceptance criteria testable
- [ ] User has signed off

### Design gate (full only)
- [ ] Pipeline and model design documented
- [ ] Data lineage and quality checks defined
- [ ] Security and PII handling reviewed
- [ ] User has signed off

### Final delivery gate (auto-approve if small)
- [ ] Quality checks pass
- [ ] Governance and PII handling cleared
- [ ] Results validated honestly
- [ ] Documentation complete
- [ ] User has signed off (full only; small auto-approves if all above pass)
