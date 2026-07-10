---
name: raci-matrix
load-when: Assigning roles, clarifying responsibilities, resolving ownership conflicts
skip-when: Project planning (see pmbok-framework), collaboration details (see collaboration.md)
---

# RACI Matrix

## Quick Reference
- **R**esponsible: does the work
- **A**ccountable: owns the outcome (one per task)
- **C**onsulted: provides input before decision
- **I**nformed: notified after decision
- Every task must have exactly one A
- Use to resolve ambiguity about who does what

## Deep Dive

### RACI Matrix Example
| Task | Lead | PM | Dev | QA | Security |
|------|------|-----|-----|-----|----------|
| Define requirements | A | R | C | C | I |
| Design architecture | A | I | R | I | C |
| Implement feature | I | I | A/R | I | I |
| Write tests | I | I | C | A/R | I |
| Security review | I | I | C | I | A/R |
| Deploy | A | I | R | I | C |

### Rules
- Every row must have exactly one A (accountable)
- Every row must have at least one R (responsible)
- C and I are optional
- A and R can be the same person
- Minimize C (too many consultants slows decisions)

### Common Mistakes
- No A: nobody owns the outcome
- Multiple A's: split ownership, confusion
- No R: nobody does the work
- Too many C's: decision paralysis
- A does all the R work: micromanagement

### When to Use RACI
- New team formation
- Process redesign
- Project kickoff
- When ownership is ambiguous
- After organizational changes

## See Also
- **pmbok-framework** — Project management context
- **scrum-guide** — Agile role definitions
- **raid-log-management** — Tracking risks and issues
- **collaboration.md** — Atlas team ownership matrix
