---
name: atlas-data-analyst-playbook
description: Analytics methodology for atlas-data-analyst: metrics, SQL, and visualization. Use when atlas-data-analyst runs.
disable-model-invocation: true
---

# Data and BI analyst playbook

Standards: clear metric definition, SQL optimization, visualization principles (clarity over decoration).

## Metrics
Define each metric precisely: numerator, denominator, grain, and filters. Agree definitions before reporting.

## SQL
Filter early, select only needed columns, use indexes, avoid needless joins. Validate row counts and edge cases.

## Visualization
Choose the chart for the question. Label axes and units. Remove clutter. Do not mislead with scales.

## Analysis artifact
Queries, metrics, findings, and a clear visualization or summary. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/analysis.md`.

## References
- https://www.edwardtufte.com/tufte/
