---
name: kimball-dimensional-modeling
load-when: Designing data warehouses, building dimensional models, ETL pipeline design
skip-when: Data quality (see great-expectations), data pipelines (see apache-airflow-patterns)
---

# Kimball Dimensional Modeling

## Quick Reference
- Fact tables: numeric measurements (foreign keys + measures)
- Dimension tables: descriptive attributes (primary key + attributes)
- Star schema: one fact table joined to dimension tables
- Slowly changing dimensions (SCD): how to handle changing attributes
- Conformance: shared dimensions across fact tables

## Deep Dive

### Dimensional Model Structure
**Fact Table**: contains foreign keys to dimensions and numeric measures.
- Additive measures: can be summed across all dimensions
- Semi-additive: can be summed across some dimensions
- Non-additive: cannot be summed (ratios, percentages)

**Dimension Table**: contains descriptive attributes for filtering/grouping.
- Conformed dimensions: shared across multiple fact tables
- Junk dimensions: many small flags packed into one dimension
- Role-playing dimensions: same dimension used multiple ways (date as order date, ship date)

### Star Schema
```
Sales (fact)
  ├── Date (dimension)
  ├── Product (dimension)
  ├── Store (dimension)
  └── Customer (dimension)
```

### Slowly Changing Dimensions (SCD)
| Type | Method | Use When |
|------|--------|----------|
| Type 1 | Overwrite | History doesn't matter |
| Type 2 | Add new row | History matters, track changes |
| Type 3 | Add new column | Limited history (last N changes) |

### Kimball's Process
1. **Choose the process**: select business process to model
2. **Declare the grain**: what one row represents
3. **Identify dimensions**: who/what/where/when
4. **Identify facts**: what happened (measures)

### Conformed Dimensions
Shared dimensions that allow joining multiple fact tables:
- Same structure, same values, same business rules
- Enable cross-process analysis (sales + inventory + returns)

### ETL Best Practices
- Extract: source system extraction with change detection
- Transform: business rules, cleansing, conforming
- Load: populate fact and dimension tables in correct order
- Dimension first, then fact (facts reference dimensions)

## See Also
- **dbt-best-practices** — Modern data transformation
- **great-expectations** — Data quality validation
- **apache-airflow-patterns** — Orchestration of ETL pipelines
- **data-anti-patterns** — Common data warehouse failures
