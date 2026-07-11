---
name: c4-model
load-when: Creating architecture diagrams, documenting system structure, communicating design
skip-when: Detailed architecture decisions (see architecture-decision-records), trade-offs (see trade-off-analysis)
---

# C4 Model

## Quick Reference
- Four levels: Context → Container → Component → Code
- Each level zooms in one step
- Start at Context, go deeper only when needed
- Use for onboarding, documentation, architecture reviews
- Notation: boxes (components), lines (relationships), people (users)

## Deep Dive

### Level 1: Context
The big picture. Shows the system and its relationships to users and external systems.

- **System**: your application
- **People**: users, admins, external actors
- **External Systems**: databases, APIs, third-party services
- **Relationships**: how they interact

### Level 2: Container
Zoom into the system boundary. Shows deployable units.

- **Web App**: browser-based UI
- **API**: REST/GraphQL backend
- **Database**: data store
- **Message Queue**: async communication
- **Cache**: performance optimization

### Level 3: Component
Zoom into a container. Shows major building blocks.

- **Controllers**: handle HTTP requests
- **Services**: business logic
- **Repositories**: data access
- **Validators**: input validation

### Level 4: Code
Optional. Shows class diagrams or key abstractions.

### Benefits
- **Onboarding**: new team members understand the system fast
- **Documentation**: always up-to-date if maintained
- **Architecture reviews**: shared vocabulary for discussions
- **Decision context**: shows what a decision affects

### When to Use Each Level
| Level | When to Use |
|-------|-------------|
| Context | New project kickoff, stakeholder presentations |
| Container | Team onboarding, deployment planning |
| Component | Detailed design, API documentation |
| Code | Complex algorithms, inheritance hierarchies |

### Diagramming Tips
- Keep each diagram focused on one level
- Use consistent notation across diagrams
- Add a legend for custom symbols
- Include dates and version numbers
- Store diagrams near the code they describe

## See Also
- **architecture-decision-records** — Documenting why, not just what
- **trade-off-analysis** — Evaluating architectural options
- **swebok** — Software engineering body of knowledge
- **domain-driven-design** — Modeling complex domains
