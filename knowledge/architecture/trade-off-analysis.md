---
name: trade-off-analysis
load-when: Evaluating architectural options, comparing technical approaches, documenting decisions
skip-when: Making the decision (see architecture-decision-records), creating diagrams (see c4-model)
---

# Trade-Off Analysis

## Quick Reference
- Every decision has trade-offs — explicitly evaluate them
- Use weighted scoring to compare options objectively
- Document trade-offs in ADRs for future reference
- Involve stakeholders in trade-off discussions
- Revisit trade-offs as requirements change

## Deep Dive

### Why Trade-Off Analysis Matters
There's no perfect solution. Every technical decision sacrifices something. Trade-off analysis makes these sacrifices explicit so the team can make informed choices.

### Weighted Scoring Matrix
1. Identify options (A, B, C)
2. Define criteria (performance, cost, maintainability, etc.)
3. Weight criteria by importance (1-5)
4. Score each option per criterion (1-5)
5. Calculate weighted scores
6. Choose highest score (or discuss if scores are close)

Example:
| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Performance | 5 | 4 (20) | 3 (15) | 5 (25) |
| Cost | 4 | 3 (12) | 5 (20) | 2 (8) |
| Maintainability | 3 | 5 (15) | 3 (9) | 3 (9) |
| **Total** | | **47** | **44** | **42** |

### Common Trade-Offs in Software
| Trade-Off | Description |
|-----------|-------------|
| Speed vs Accuracy | Fast inference vs precise results |
| Simplicity vs Flexibility | Easy now vs extensible later |
| Cost vs Performance | Cheaper infra vs faster response |
| Build vs Buy | Custom solution vs vendor dependency |
| Consistency vs Availability | CAP theorem in distributed systems |
| Security vs Usability | More auth steps vs smoother UX |

### Decision Matrices
For complex decisions, use a decision matrix:
1. List options as columns
2. List criteria as rows
3. Add weights and scores
4. Calculate and compare

### Revisiting Trade-Offs
Trade-offs aren't permanent. Revisit when:
- Requirements change
- Technology evolves
- Team expertise grows
- Performance bottlenecks emerge

## See Also
- **architecture-decision-records** — Documenting the chosen trade-off
- **c4-model** — Visualizing what the decision affects
- **mece-framework** — Structuring criteria without overlap
- **domain-driven-design** — Trade-offs in domain modeling
