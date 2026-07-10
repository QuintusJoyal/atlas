---
name: atlas-dba-playbook
description: Database playbook for atlas-dba.
type: playbook
appliesTo: [atlas-dba]
tags: [playbook, dba, schema, tuning]
---

# atlas-dba

## Route
- schema design, migrations → dba
- query tuning, indexing → dba
- backup, recovery, HA/DR → dba
- data integrity → dba
- PostgreSQL/database operations → dba

## Knowledge
- Kimball dimensional modeling → k/kimball-dimensional-modeling
- PostgreSQL documentation → k/kimball-dimensional-modeling
- Great Expectations (data quality) → k/great-expectations

## Scope
schema design, query tuning, indexing, backup/recovery, HA/DR, database operations | NOT data pipelines (→ data-eng), analytics (→ data-analyst), application code (→ dev), cloud architecture (→ cloud)

## Delegation Examples
### Real-time analytics DB
"Set up analytics database." → dba + data-eng in parallel: schema design + ingestion pipeline must coordinate.

### Data corruption
"Production DB corrupted, no recent backups." → dba: assess WAL/archival recovery, point-in-time recovery feasibility, data integrity verification before remediation.
