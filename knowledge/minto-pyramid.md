---
name: minto-pyramid
load-when: Structuring documents, writing proposals, organizing complex information
skip-when: Problem analysis (see mece-framework), questioning (see socratic-method)
---

# Minto Pyramid Principle

## Quick Reference
- Start with the answer/conclusion first
- Group supporting arguments into MECE categories
- Each level summarizes the level below
- Use for proposals, reports, emails, presentations
- Forces clear thinking before writing

## Deep Dive

### Structure
```
Conclusion (top)
├── Argument 1
│   ├── Supporting detail 1a
│   └── Supporting detail 1b
├── Argument 2
│   ├── Supporting detail 2a
│   └── Supporting detail 2b
└── Argument 3
    ├── Supporting detail 3a
    └── Supporting detail 3b
```

### Rules
1. **Start with the answer**: don't bury the conclusion
2. **Group ideas MECE**: no overlap, complete coverage
3. **Use logical order**: time order, structural order, importance order
4. **Summarize at each level**: each heading summarizes the section below

### When to Use
- **Proposals**: recommendation → reasons → evidence
- **Reports**: conclusion → analysis → data
- **Emails**: ask → context → action items
- **Presentations**: thesis → arguments → supporting data

### Top-Down vs Bottom-Up
- **Top-down**: start with conclusion, build supporting structure (for presenting)
- **Bottom-up**: gather all facts, find the pattern, state conclusion (for analysis)

### Example
```markdown
# Recommendation
We should migrate to PostgreSQL.

## Reason 1: Better JSON support
- JSONB type for document storage
- Indexing on JSON fields
- 40% faster queries on document data

## Reason 2: Cost savings
- No license fees (vs Oracle)
- Reduced DBA costs
- Estimated $50K/year savings

## Reason 3: Community and ecosystem
- Active open-source community
- Rich extension ecosystem
- Strong hiring pool
```

## See Also
- **mece-framework** — MECE is foundational to the pyramid
- **spin-selling** — Structured discovery before writing
- **socratic-method** — Questioning before conclusions
- **raid-log-management** — Structuring risk/issue reports
