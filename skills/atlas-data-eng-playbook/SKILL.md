---
name: atlas-data-eng-playbook
description: Data engineering playbook for atlas-data-eng.
type: playbook
appliesTo: [atlas-data-eng]
tags: [playbook, data-eng, pipelines]
---

# atlas-data-eng

## Route
- data pipelines → data-eng
- ETL/ELT design → data-eng
- data modeling → data-eng
- data quality → data-eng
- streaming infrastructure → data-eng

## Knowledge
- Kimball dimensional modeling → k/kimball-dimensional-modeling
- dbt best practices → k/dbt-best-practices
- Apache Airflow patterns → k/apache-airflow-patterns
- Great Expectations → k/great-expectations

## Scope
data pipelines, ETL/ELT, data modeling, data quality, streaming | NOT analytics (→ data-analyst), ML models (→ data-sci), database operations (→ dba), application code (→ dev)

## Delegation Examples
### Real-time analytics platform
"Build streaming analytics." → data-eng + data-sci in parallel: pipeline design + feature engineering requirements are co-dependent.

### Silent data loss
"Pipeline dropped 2 hours of data." → data-eng: investigate schema drift root cause, retroactive backfill, add schema validation guards.
