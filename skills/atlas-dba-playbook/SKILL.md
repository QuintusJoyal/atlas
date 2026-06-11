---
name: atlas-dba-playbook
description: Database methodology for atlas-dba: schema, tuning, and recovery. Use when atlas-dba runs.
disable-model-invocation: true
---

# Database administrator playbook

Standards: normalization, indexing and query tuning, ACID, backup with HA and DR.

## Schema
Normalize to remove redundancy, denormalize only with a measured reason. Choose keys and constraints deliberately.

## Performance
Index for the real query patterns. Read query plans. Avoid N+1. Measure before and after.

## Reliability
Backup strategy with tested restore. Define RPO and RTO. Plan high availability and failover.

## Database artifact
Schema, indexing and tuning decisions, backup and recovery plan. Persist to `.atlas/runs/<run-id>/dba.md`.

## References
- https://www.postgresql.org/docs/current/index.html
