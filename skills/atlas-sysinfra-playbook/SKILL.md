---
name: atlas-sysinfra-playbook
description: Systems playbook for atlas-sysinfra.
type: playbook
appliesTo: [atlas-sysinfra]
tags: [playbook, sysinfra, hardening]
---

# atlas-sysinfra

## Route
- server hardening → sysinfra
- virtualization, capacity planning → sysinfra
- backup, recovery → sysinfra
- CIS Benchmark application → sysinfra
- operational runbooks → sysinfra

## Knowledge
- CIS Benchmarks → k/cis-benchmarks
- ITIL incident management → k/itil-incident-management
- AWS/Azure Well-Architected → k/aws-well-architected

## Scope
server hardening, virtualization, capacity planning, backup/recovery, operational runbooks | NOT network topology (→ network), cloud architecture (→ cloud), deployment (→ devops), application code (→ dev)

## Delegation Examples
### Full hybrid setup
"Hybrid environment provisioning." → sysinfra + network in parallel: server hardening + host firewalls must align with network rules.

### Compromised server
"Server compromised, need forensics." → sysinfra: capture disk images, memory dumps, logs BEFORE remediation.
