---
name: dbt-best-practices
load-when: Building data transformations, organizing dbt projects, testing data models
skip-when: Data warehouse design (see kimball-dimensional-modeling), orchestration (see apache-airflow-patterns)
---

# dbt Best Practices

## Quick Reference
- Three layers: staging → intermediate → marts
- Staging: 1:1 with source tables, light transformations
- Intermediate: business logic, joins, calculations
- Marts: final business-ready datasets
- Test everything: not-null, unique, relationships, custom
- Document everything: descriptions on models and columns

## Deep Dive

### Project Structure
```
models/
  staging/        # 1:1 with sources
  intermediate/   # business logic
  marts/          # final datasets
```

### Staging Layer
- One model per source table
- Rename columns for consistency
- Cast types
- Filter and clean
- No business logic

### Intermediate Layer
- Apply business rules
- Join across sources
- Calculate derived fields
- Handle SCDs

### Marts Layer
- Final business-ready datasets
- One mart per business process
- Optimized for analytics
- Well-documented

### Testing
```yaml
models:
  - name: orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - relationships:
              to: ref('customers')
              field: id
```

### Documentation
- Add descriptions to all models and columns
- Use `docs` blocks for complex descriptions
- Generate and host docs with `dbt docs generate`

### Materializations
- **View**: thin, fast, good for staging
- **Table**: full refresh, good for small marts
- **Incremental**: append/update, good for large fact tables
- **Ephemeral**: CTE, good for shared logic

### Lineage
- Use `ref()` for all model references
- dbt automatically builds DAG from refs
- Visualize lineage to understand data flow

## See Also
- **kimball-dimensional-modeling** — Dimensional model design
- **great-expectations** — Data quality validation
- **apache-airflow-patterns** — Orchestrating dbt runs
- **data-anti-patterns** — Common data transformation failures
