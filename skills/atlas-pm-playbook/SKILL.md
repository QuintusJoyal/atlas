---
name: atlas-pm-playbook
description: Product management playbook for atlas-pm.
type: playbook
appliesTo: [atlas-pm]
tags: [playbook, pm, user-stories]
---

# atlas-pm

## Route
- requirements, user stories → pm
- prioritization, backlog grooming → pm
- scope definition → pm
- stakeholder alignment → pm
- definition of done → pm

## Knowledge
- INVEST criteria, RICE, MoSCoW → k/babok-techniques
- Scrum practices → k/scrum-guide
- User story format → k/bdd-gherkin
- Structured communication → k/minto-pyramid

## Scope
requirements, user stories, acceptance criteria, prioritization, scope definition, definition of ready/done | NOT implementation (→ dev), technical design (→ architect), testing (→ qa), security (→ security)

## Delegation Examples
### Feature intake
"New user dashboard." → pm: write PRD with user stories, acceptance criteria, MoSCoW priority. Gate: requirements approved by user.

### Ambiguous request
"Users are confused." → pm: interview user, scope problem, define success metrics. Do not write stories until problem is bounded.

### Multi-role coordination
"Feature spans multiple teams." → pm + architect in parallel: pm defines scope/value, architect assesses feasibility/cost.
