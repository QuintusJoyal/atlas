# Workflow: data-project

Data or analytics work. Pulls the data roles into the chain.

## Phases and roles
1. Requirements: atlas-pm, atlas-ba
2. Gate 1: requirements (user)
3. Design: atlas-data-eng (pipelines), atlas-dba (storage), atlas-data-sci (modeling if needed), atlas-architect for system fit
4. Gate 2: design (user)
5. Build: atlas-data-eng, atlas-data-sci
6. Analysis and validation: atlas-data-analyst, atlas-qa (data-quality checks)
7. Security and compliance: atlas-security, atlas-compliance (data governance, PII)
8. Gate 3: final delivery (user)
9. Deploy and monitor: atlas-devops

## Default tiers
Premium: atlas-architect, atlas-security, atlas-compliance. Standard: atlas-data-eng, atlas-data-sci, atlas-dba. Fast: atlas-data-analyst.

## Definition of Done per gate
- Requirements: data sources, grain, and metric definitions agreed.
- Design: pipeline and model design, lineage, and data-quality checks defined.
- Final delivery: quality checks pass; governance and PII handling cleared; results validated honestly.
