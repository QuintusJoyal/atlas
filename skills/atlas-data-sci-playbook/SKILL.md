---
name: atlas-data-sci-playbook
description: Data science methodology for atlas-data-sci: CRISP-DM, evaluation, and MLOps. Use when atlas-data-sci runs.
disable-model-invocation: true
---

# Data scientist and ML playbook

Standards: CRISP-DM, rigorous model evaluation, MLOps (continuous delivery for machine learning), bias and fairness checks.

## CRISP-DM
Business understanding, data understanding, data preparation, modeling, evaluation, deployment.

## Evaluation
Pick the metric that matches the goal. Use a held-out set. Report honestly, including failure modes and uncertainty. No cherry-picking.

## MLOps
Version data, code, and models. Track experiments. Make training reproducible. Monitor for drift.

## Fairness
Check for bias across relevant groups. Document limitations.

## Data-science artifact
Problem framing, approach, evaluation plan and results, risks. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/data-sci.md`.

## References
- https://www.crisp-dm.org/
- https://ml-ops.org/
