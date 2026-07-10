---
name: atlas-cloud-playbook
description: Cloud methodology for atlas-cloud: well-architected design, landing zones, and FinOps. Use when atlas-cloud runs.
disable-model-invocation: true
---

# Cloud architect playbook

Standards: cloud well-architected pillars (operational excellence, security, reliability, performance, cost, sustainability), landing zones, FinOps Foundation principles.

## Design
Start from requirements and NFRs. Choose managed services over custom where they fit. Diagram in mermaid. Justify each service.

## Landing zone
Account and environment structure, identity and access, network baseline, guardrails, logging.

## FinOps
Estimate cost up front. Tag resources. Prefer autoscaling and right-sizing. Flag cost risks.

## Security
Least privilege, encryption in transit and at rest, secrets management, and audit logging.

## Cloud artifact
Architecture, landing-zone and security decisions, cost estimate, trade-offs. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/cloud.md`.

## References
- https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
- https://www.finops.org/framework/
