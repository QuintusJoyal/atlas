---
name: api-design
description: API-first design with OpenAPI. Design, implement, test, document.
type: pipeline
triggers:
  - api-design
  - new-endpoint
  - rest-api
  - graphql
variants:
  small:
    description: Simple endpoint, no design phase.
    gates: [final]
    skip: [design]
    token-estimate: light
    kickoff: lightweight
    auto-approve: true
    tracking: none
  full:
    description: Complex API with multiple endpoints, design review required.
    gates: [design, final]
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

# Workflow: api-design

API-first design with OpenAPI specification. Design, implement, test, document.

## Variant selection

- **small:** single endpoint, simple request/response
- **full:** multiple endpoints, complex schema, authentication, versioning

## Phase 0: Kickoff

- **Standard:** create run folder, seed team.json, estimation huddle, write budget.md, gate: token-budget if heavy
- **Lightweight:** create run folder, start immediately (no tracking)

## Phases

### design
- **Gate:** design
- **Parallel:** true
- **Roles:** atlas-architect (premium), atlas-dev (standard)
- **Skip-if:** variant=small
- **Input:** API requirements, existing API patterns
- **Output:** OpenAPI spec, API design document (endpoints, schemas, error codes)

### implement
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (fast)
- **Input:** OpenAPI spec, API design document (full) or API requirements (small)
- **Output:** implementation summary (endpoints implemented, files changed)

### test
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-qa (standard)
- **Input:** implementation summary, OpenAPI spec
- **Output:** test results (contract tests, integration tests, error handling)

### document
- **Gate:** final
- **Parallel:** false
- **Roles:** atlas-docs (standard)
- **Input:** OpenAPI spec, implementation summary
- **Output:** API documentation (README, usage examples, changelog)

## Definition of Done per gate

### Design gate (full only)
- [ ] OpenAPI spec valid and complete
- [ ] Endpoints, schemas, and error codes reviewed
- [ ] Versioning and backward-compatibility approach agreed
- [ ] User has signed off on the API design

### Final gate (auto-approve if small)
- [ ] OpenAPI spec matches the implementation
- [ ] All endpoints implemented per spec
- [ ] Contract tests passing
- [ ] Error handling per spec (correct status codes, error schemas)
- [ ] API documentation complete
- [ ] User has signed off (full only; small auto-approves if all above pass)
