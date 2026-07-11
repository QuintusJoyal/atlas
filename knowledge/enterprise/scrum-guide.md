---
name: scrum-guide
load-when: Running sprints, defining Scrum roles, planning iterations
skip-when: Project planning (see pmbok-framework), requirements (see babok-techniques)
---

# Scrum Guide

## Quick Reference
- 3 roles: Product Owner, Scrum Master, Developers
- 5 events: Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective
- 3 artifacts: Product Backlog, Sprint Backlog, Increment
- Sprint: fixed timebox (1-4 weeks), produces a done increment
- Empiricism: transparency, inspection, adaptation

## Deep Dive

### Roles
| Role | Responsibility |
|------|---------------|
| Product Owner | Maximize value, manage Product Backlog |
| Scrum Master | Enable Scrum, remove impediments, coach |
| Developers | Build the Increment, self-managing |

### Events
| Event | Purpose | Timebox |
|-------|---------|---------|
| Sprint | Build a done increment | 1-4 weeks |
| Sprint Planning | Plan the Sprint | 8 hours (1-month Sprint) |
| Daily Scrum | Inspect progress | 15 minutes |
| Sprint Review | Demo and gather feedback | 4 hours (1-month Sprint) |
| Sprint Retrospective | Improve process | 3 hours (1-month Sprint) |

### Artifacts
- **Product Backlog**: ordered list of everything needed in the product
- **Sprint Backlog**: selected items + plan for delivering the Increment
- **Increment**: the sum of all completed Product Backlog items

### Sprint Planning
1. Why is this Sprint valuable? (Product Owner)
2. What can be Done? (Developers select items)
3. How will the done work be achieved? (Developers plan)

### Definition of Done
Shared understanding of what "done" means:
- Code reviewed
- Tests passing
- Documentation updated
- Deployed to staging
- Acceptance criteria met

### Sprint Retrospective
- What went well?
- What could be improved?
- What will we commit to improving?

### Anti-Patterns
- Sprint without a goal
- Daily Scrum as status report
- Retrospective without action items
- Product Owner dictating implementation

## See Also
- **pmbok-framework** — Traditional project management
- **definition-of-done** — Completion criteria
- **babok-techniques** — Requirements management
- **mece-framework** — Sprint planning decisions
