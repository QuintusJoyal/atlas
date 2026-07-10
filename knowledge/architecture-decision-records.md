---
name: architecture-decision-records
load-when: Making design decisions, documenting architecture rationale, reviewing past decisions
skip-when: Creating diagrams (see c4-model), evaluating options (see trade-off-analysis)
---

# Architecture Decision Records (ADR)

## Quick Reference
- ADR = a short document recording one architecture decision
- Format: Title, Status, Context, Decision, Consequences
- One ADR per significant decision
- Store ADRs in the repo alongside the code
- Never delete ADRs — mark as superseded instead

## Deep Dive

### ADR Template
```markdown
# ADR-001: Use PostgreSQL as primary database

## Status
Accepted

## Context
We need a relational database for the core application data. 
Requirements: ACID compliance, JSON support, strong community.

## Decision
Use PostgreSQL 16 as the primary database.

## Consequences
+ Excellent JSON support (JSONB)
+ Strong ACID compliance
+ Large ecosystem of extensions
- Requires DBA expertise for performance tuning
- Migration from existing MySQL requires data conversion
```

### When to Write an ADR
- Choosing a framework, language, or library
- Defining API contracts
- Making data storage decisions
- Adopting new tools or processes
- Changing deployment strategy
- Any decision you'd want to explain to a future team member

### When NOT to Write an ADR
- Trivial implementation details
- Temporary workarounds
- Decisions that are clearly obvious

### ADR Lifecycle
1. **Proposed**: draft the ADR, get feedback
2. **Accepted**: decision is made and agreed upon
3. **Deprecated**: the decision is no longer valid
4. **Superseded**: replaced by a newer ADR (reference the new one)

### Numbering
Sequential: ADR-001, ADR-002, etc. Never reuse numbers.

### Best Practices
- Keep ADRs short (1-2 pages max)
- Write for your future self
- Include the "why" not just the "what"
- Store in `docs/adr/` or `docs/architecture/`
- Reference ADRs in code comments and PR descriptions

## See Also
- **c4-model** — Documenting what was decided (diagrams)
- **trade-off-analysis** — Evaluating options before deciding
- **domain-driven-design** — Modeling decisions in complex domains
- **swebok** — Software engineering knowledge areas
