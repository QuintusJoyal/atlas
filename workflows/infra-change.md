# Workflow: infra-change

Infrastructure, network, or cloud changes. Mandatory security gate.

## Phases and roles
1. Requirements: atlas-pm or atlas-delivery
2. Gate 1: requirements (user)
3. Design: atlas-cloud, atlas-sysinfra, atlas-network (as relevant), atlas-ent-arch for cross-system fit
4. Gate 2: design (user)
5. Implementation: atlas-devops (IaC), atlas-sysinfra, atlas-network
6. Security gate: atlas-security (mandatory), atlas-compliance if regulated
7. Gate 3: final delivery (user)
8. Apply and verify: atlas-devops with rollback ready
9. Monitoring handoff: atlas-maintenance

## Default tiers
Premium: atlas-cloud, atlas-ent-arch, atlas-security. Standard: atlas-devops, atlas-sysinfra, atlas-network.

## Definition of Done per gate
- Requirements: target state and constraints clear; blast radius understood.
- Design: architecture, security controls, and cost noted; rollback planned.
- Final delivery: security cleared; change reversible; observability and alerts in place.
