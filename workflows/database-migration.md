---
name: database-migration
description: Schema migration with forward/backward compatibility, data validation, staged rollout, and cutover.
type: standard
triggers:
  - schema-change
  - database-migration
  - data-model-update
variants:
  small:
    description: Simple schema change, backward-compatible, no data migration needed.
    gates: [final]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Complex migration with data transformation, backward compatibility concerns, or zero-downtime requirement.
    gates: [design, final]
    token-estimate: medium
    kickoff: standard
    auto-approve: false
    tracking: full
conditions:
  - if: data-changes
    add: [data-validation]
    add-roles: [atlas-data-eng]
  - if: regulated
    add: [compliance]
    add-roles: [atlas-compliance]
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: database migration

Schema changes are high-risk. Design for reversibility. Test with production-like data.

## Variant selection

Pick variant based on migration complexity:
- **small:** additive change (new column with default, new index), backward-compatible, no data backfill
- **full:** column rename/remove, data backfill, zero-downtime requirement, or cross-service schema dependency

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, write budget.md
- **Lightweight:** create run folder, start immediately

## Phases

### schema-review
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dba (standard), atlas-architect (standard if cross-service impact)
- **Input:** proposed schema change, current schema, affected queries
- **Output:** schema-review.md (DDL, backward compatibility assessment, affected services, rollback DDL)

### migration-implementation
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dba (standard), atlas-dev (fast for query updates)
- **Input:** schema-review.md, application code
- **Output:** implementation summary (migration scripts, updated queries, test results)

### data-validation
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-qa (standard), atlas-dba (standard)
- **Input:** implementation summary, migration scripts
- **Output:** validation report (data integrity checks, row counts, constraint verification)

### staged-rollout
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-devops (standard)
- **Input:** validated migration, rollback plan
- **Output:** deployment artifact (migration execution plan, staging verification, production rollout schedule)

### cutover
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-dba (standard), atlas-devops (standard)
- **Input:** staging validation, production approval
- **Output:** cutover report (migration executed, data verified, rollback status)

## Definition of Done

- [ ] Schema change is backward-compatible (or has explicit migration strategy)
- [ ] Rollback DDL exists and has been tested on staging
- [ ] Data validation checks pass (row counts, constraints, integrity)
- [ ] Zero-downtime strategy verified if applicable
- [ ] Affected application queries updated and tested
- [ ] User has signed off on cutover (full only; small auto-approves)
