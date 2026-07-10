---
name: atlas-data-eng-playbook
description: Data engineering methodology for atlas-data-eng: pipelines, modeling, and data quality. Use when atlas-data-eng runs.
disable-model-invocation: true
---

# Data engineer playbook

Standards: Kimball dimensional modeling, medallion architecture (bronze, silver, gold), data quality, idempotent pipelines.

## Pipelines
Idempotent and replayable. Handle late and duplicate data. Separate ingestion, transformation, and serving.

## Modeling
Dimensional models for analytics. Medallion layers from raw to curated. Document lineage.

## Data quality
Validate schema, completeness, uniqueness, and freshness. Fail loudly on violations.

## Data-engineering artifact
Pipeline design, modeling, data-quality checks. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/data-eng.md`.

## References
- https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/
