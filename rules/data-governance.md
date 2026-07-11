---
name: data-governance
description: Data classification, retention, PII handling, lineage, and access control rules. Load when data-related work is in motion.
load: on-demand
globs: "**/*.{sql,py,ts,js,go,java}"
---

# Data governance

Data has lifecycle, access boundaries, and regulatory obligations. Treat it accordingly.

## Classification
- Classify data before processing: Public, Internal, Confidential, Restricted.
- PII and PHI are Restricted by default. Apply encryption at rest and in transit.
- Log the classification level in schema documentation or data catalog entries.

## Access control
- Apply least-privilege access to data stores. Readers should not also be writers.
- Separate production data access from development. Never use production credentials in dev.
- Audit data access for Restricted data. Record who, what, when, and purpose.

## Retention and disposal
- Define retention periods for each data classification. Document them.
- Automate deletion when possible. Manual disposal is error-prone.
- Backups follow the same retention policy. Do not retain expired data in backups.

## PII handling
- Minimize PII collection. Collect only what the use case requires.
- Pseudonymize or anonymize data used for testing or analytics.
- Reference: `k/gdpr-requirements.md` for EU data subjects.

## Data lineage
- Document where data comes from, how it transforms, and where it goes.
- Use tooling (dbt, Great Expectations) for lineage tracking where available.
- Reference: `k/great-expectations.md`, `k/dbt-best-practices.md`.

## Schema changes
- Schema migrations require atlas-dba review before execution.
- Backward-compatible changes preferred. Breaking changes need a migration plan.
- Reference: `k/kimball-dimensional-modeling.md` for analytical data modeling.
