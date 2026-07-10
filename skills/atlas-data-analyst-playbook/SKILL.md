---
name: atlas-data-analyst-playbook
description: Analytics playbook for atlas-data-analyst.
type: playbook
appliesTo: [atlas-data-analyst]
tags: [playbook, data-analyst, sql, metrics]
---

# atlas-data-analyst

## Route
- metrics definition, KPI reporting → data-analyst
- SQL queries, data exploration → data-analyst
- dashboard design → data-analyst
- data validation → data-analyst
- business insights → data-analyst

## Knowledge
- Kimball dimensional modeling → k/kimball-dimensional-modeling
- dbt best practices → k/dbt-best-practices
- Great Expectations → k/great-expectations
- Minto Pyramid (structured communication) → k/minto-pyramid

## Scope
metrics definition, SQL queries, dashboards, data validation, business insights | NOT ML models (→ data-sci), data pipelines (→ data-eng), database operations (→ dba), application code (→ dev)

## Delegation Examples
### Churn analysis
"Understand user churn." → data-analyst + data-sci in parallel: analyst defines descriptive metrics/segments, data-sci builds predictive model.

### Numbers look wrong
"Dashboard numbers don't match." → data-analyst: validate pipeline output, cross-check against source systems, produce data quality assessment before re-running analysis.
