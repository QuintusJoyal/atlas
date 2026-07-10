---
name: mece-framework
load-when: Structuring problems, organizing requirements, ensuring complete coverage
skip-when: Specific analysis (see trade-off-analysis), communication (see minto-pyramid)
---

# MECE Framework

## Quick Reference
- MECE = Mutually Exclusive, Collectively Exhaustive
- Mutually Exclusive: no overlap between categories
- Collectively Exhaustive: all possibilities covered
- Use to structure problems, requirements, and analyses
- Prevents gaps and redundancy

## Deep Dive

### What MECE Means
- **Mutually Exclusive**: each item belongs to exactly one category
- **Collectively Exhaustive**: every possible item belongs to some category

### Why MECE Matters
- Prevents double-counting (overlap)
- Prevents missed items (gaps)
- Makes analysis complete and accurate
- Simplifies decision-making

### How to Create MECE Structures
1. Start with the complete set of possibilities
2. Define categories that don't overlap
3. Verify: can any item belong to two categories? (mutually exclusive)
4. Verify: is every possible item covered? (collectively exhaustive)

### Common MECE Structures
- **By time**: past, present, future
- **By geography**: North, South, East, West
- **By product**: Product A, Product B, Product C
- **By customer type**: new, existing, returning
- **By process step**: design, build, test, deploy

### Example
Revenue breakdown:
- Product sales (mutually exclusive from services)
- Services (mutually exclusive from product sales)
- Together: all revenue (collectively exhaustive)

### Non-MECE Example
Revenue breakdown:
- Online sales (overlaps with domestic sales)
- Domestic sales (overlaps with online sales)
- Not MECE: online and domestic overlap

## See Also
- **minto-pyramid** — Structuring communication using MECE
- **trade-off-analysis** — Applying MECE to evaluation criteria
- **5-whys-root-cause** — MECE in root cause analysis
- **spin-selling** — Structured questioning
