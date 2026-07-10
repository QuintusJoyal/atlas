---
name: atlas-network-playbook
description: Network playbook for atlas-network.
type: playbook
appliesTo: [atlas-network]
tags: [playbook, network, zero-trust]
---

# atlas-network

## Route
- network topology, segmentation → network
- zero-trust architecture → network
- VPN, firewall rules → network
- DNS strategy → network
- hybrid connectivity → network

## Knowledge
- NIST SP 800-207 zero trust → k/nist-800-53-controls
- CIS Benchmarks → k/cis-benchmarks
- AWS/Azure networking → k/aws-well-architected

## Scope
network topology, segmentation, zero-trust, VPN, firewalls, DNS, monitoring | NOT server hardening (→ sysinfra), cloud architecture (→ cloud), deployment (→ devops)

## Delegation Examples
### Hybrid network design
"Full hybrid environment." → network + cloud in parallel: topology/VPC design, addressing/routing alignment.

### DNS issues
"DNS propagation affecting production." → network: diagnose split-horizon misconfiguration, fix without downtime.
