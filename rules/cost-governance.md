---
name: cost-governance
description: Cloud cost governance: budgets, rightsizing, reserved capacity, tagging. Load when cost or cloud optimization tasks are in motion.
load: on-demand
---

# Cost governance

Cloud spend is real money. Treat it with the same rigor as security.

## Tagging and allocation
- Tag all cloud resources with: owner, environment, cost-center, purpose.
- Enforce tagging via policy (AWS Service Control Policy, Azure Policy, GCP Organization Policy).
- Untagged resources are review candidates for decommission.

## Budgets and alerts
- Set budgets per project, team, or environment. Alert at 80% and 100% thresholds.
- Review spend weekly. Investigate anomalies within 24 hours.
- Reference: `k/finops-practices.md`.

## Rightsizing
- Review instance utilization monthly. Downsize underutilized instances.
- Use auto-scaling for variable workloads. Fixed capacity wastes money during low traffic.
- Consider spot/preemptible instances for fault-tolerant workloads.

## Reserved capacity
- Commit to reserved instances or savings plans for stable, predictable workloads.
- Calculate break-even: reserved pricing vs on-demand. Typically 1-2 year commitment.
- Track reserved instance utilization and coverage.

## Decommissioning
- Remove unused resources: idle load balancers, unattached volumes, unused IPs.
- Automate cleanup via scheduled scripts or cloud-native tools.
- Archive data before deleting storage resources.

## Cost review
- Include cost estimate in architecture decisions. Reference: `k/finops-practices.md`.
- When proposing infrastructure changes, state the cost impact.
- Escalate unexpected cost spikes to the user immediately.
