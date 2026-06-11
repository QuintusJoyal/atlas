---
name: atlas-network-playbook
description: Network methodology for atlas-network: topology, segmentation, and zero-trust. Use when atlas-network runs.
disable-model-invocation: true
---

# Network engineer playbook

Standards: OSI model, network segmentation, zero-trust architecture (NIST 800-207), secure-by-design connectivity.

## Design
Map topology, trust zones, and data paths. Segment by sensitivity. Default deny; allow by explicit rule. Diagram in mermaid.

## Zero-trust principles
Verify explicitly, least privilege, assume breach. No implicit trust by network location.

## Controls
Firewalls and security groups, VPN or private connectivity, DNS strategy, monitoring and logging of flows.

## Network artifact
Topology, segmentation, controls, risks. Persist to `.atlas/runs/<run-id>/network.md`.

## References
- https://csrc.nist.gov/publications/detail/sp/800-207/final
