---
name: atlas-cloud-playbook
description: Cloud playbook for atlas-cloud.
type: playbook
appliesTo: [atlas-cloud]
tags: [playbook, cloud, finops]
---

# atlas-cloud

## Route
- cloud architecture → cloud
- landing zone design → cloud
- cost optimization → cloud
- service selection → cloud
- migration planning → cloud

## Knowledge
- AWS Well-Architected Framework → k/aws-well-architected
- Azure Well-Architected Framework → k/azure-well-architected
- FinOps practices → k/finops-practices
- CIS Benchmarks → k/cis-benchmarks

## Scope
cloud architecture, landing zones, cost optimization, service selection, migration planning | NOT network topology (→ network), server hardening (→ sysinfra), deployment (→ devops), application code (→ dev)

## Delegation Examples
### Cloud migration
"Move to cloud." → cloud + network in parallel: landing zone + VPN/Direct Connect must be planned together.

### Sovereign cloud
"Deploy to restricted region." → cloud: evaluate compliance certifications, data residency controls, regional service availability gaps.
