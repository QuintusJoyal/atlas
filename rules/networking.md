---
name: networking
description: Network design guardrails: topology, DNS, load balancing, firewalls, connectivity. Load when networking tasks are in motion.
load: on-demand
globs: "**/*.{yaml,yml,tf,hcl,sh,json}"
---

# Networking

Network design decisions affect security, performance, and operability. Design for failure.

## Topology
- Design networks for failure isolation. Separate tiers (web, app, data) into distinct subnets.
- Use private subnets for internal services. No direct internet exposure without justification.
- Document network topology: CIDR ranges, routing rules, and firewall boundaries.

## DNS and service discovery
- Use consistent DNS naming conventions. Internal services resolve via private DNS.
- TTL values: short (60s) for services with failover, longer (300s) for stable endpoints.
- Document DNS records alongside infrastructure-as-code.

## Load balancing
- Health checks must verify actual service health, not just port availability.
- Use connection draining for graceful shutdown during deployments.
- Choose algorithm by use case: round-robin for uniform backends, least-connections for variable workloads.

## Firewalls and security groups
- Default deny. Allow only what is explicitly needed.
- Review firewall rules quarterly. Remove stale rules.
- Use security groups over network ACLs where possible for easier management.

## Connectivity
- VPN or private links for cross-account or cross-region communication.
- Never expose management ports (SSH, RDP) to the public internet. Use bastion hosts or SSM.
- Document all ingress/egress points.

## Observability
- Monitor network metrics: latency, packet loss, throughput, connection count.
- Alert on anomalies: sudden latency spikes, connection exhaustion, certificate expiry.
- Reference: `k/aws-well-architected.md`, `k/cis-benchmarks.md`.
