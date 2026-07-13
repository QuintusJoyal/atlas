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
state-machine: [pending, active, gated, completed, failed, paused, aborted]
---

# Workflow: api-design

API-first design with OpenAPI specification. Design, implement, test, document.

## Variant selection

- **small:** single endpoint, simple request/response
- **full:** multiple endpoints, complex schema, authentication, versioning

## Phases

### design
- **Gate:** design
- **Parallel:** true
- **Roles:** atlas-architect (premium), atlas-dev (standard)
- **Input:** API requirements, existing API patterns
- **Output:** OpenAPI spec, API design document (endpoints, schemas, error codes)

### implement
- **Gate:** null
- **Parallel:** false
- **Roles:** atlas-dev (fast)
- **Input:** OpenAPI spec, API design document
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

## Definition of Done

- [ ] OpenAPI spec valid and complete
- [ ] All endpoints implemented per spec
- [ ] Contract tests passing
- [ ] Error handling per spec (correct status codes, error schemas)
- [ ] API documentation complete
- [ ] User has signed off
