# Infra Change (Lite)

Infrastructure changes are high-risk. Design for reversibility. Test in staging. Rollback first, analyze later. This lite version has no lite agent for atlas-devops, atlas-architect, or atlas-data-eng — if the change needs one of them, tell the user this task needs a role outside lite's 5 and suggest the full bundle.

## Phase 1: Planning
- **Roles:** atlas-architect
- **Input:** change requirements, current infrastructure
- **Output:** change plan (impact assessment, rollback plan)
- **Gate:** user approves

## Phase 2: Implementation
- **Roles:** atlas-dev (for anything lite's roster can actually implement; most infra changes need atlas-devops, which lite doesn't ship — flag this to the user)
- **Input:** change plan
- **Output:** implementation summary

## Phase 3: Validation
- **Roles:** atlas-qa
- **Input:** implementation summary
- **Output:** validation report (functionality verified)
- **Gate:** tests pass

## Phase 4: Delivery
- **Roles:** atlas-security (if security-sensitive)
- **Input:** validated change
- **Output:** deployment record
- **Gate:** user approves

## Definition of Done
- [ ] Change applied in staging first
- [ ] Rollback plan tested
- [ ] Monitoring confirms no regression
- [ ] User has signed off
