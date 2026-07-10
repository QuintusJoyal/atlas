---
name: finops-practices
load-when: Optimizing cloud costs, implementing showback/chargeback, budget management
skip-when: Cloud architecture (see aws-well-architected, azure-well-architected), deployment (see gitops-principles)
---

# FinOps Practices

## Quick Reference
- FinOps = Cloud Financial Operations
- Three phases: Inform → Optimize → Operate
- FOCUS format: open standard for cloud cost data
- Showback: attribute costs to teams without billing
- Chargeback: bill teams for their usage
- Commitment-based discounts: reserved instances, savings plans

## Deep Dive

### FinOps Lifecycle
1. **Inform**: visibility, allocation, benchmarking
2. **Optimize**: rightsizing, reserved instances, spot, cleanup
3. **Operate**: automation, governance, continuous improvement

### Cost Allocation
- Tag all resources with cost centers
- Use resource groups for logical grouping
- Implement budget alerts
- Regular cost reviews with teams

### Optimization Strategies
| Strategy | Savings | Effort |
|----------|---------|--------|
| Right-sizing | 20-40% | Low |
| Reserved instances | 30-60% | Medium |
| Spot instances | 60-90% | Medium |
| Auto-scaling | 10-30% | Low |
| Cleanup (orphaned resources) | 5-15% | Low |

### FOCUS Format
Open standard for cloud cost and usage data:
- Unified schema across providers
- Enables cross-cloud analysis
- Standardized cost categories

### FinOps Team Roles
- **FinOps Practitioner**: leads FinOps practice
- **Engineering**: implements optimization
- **Finance**: manages budgets and forecasting
- **Executive**: sets targets and reviews

### Metrics
- Cost per transaction
- Cost per user
- Cost per environment
- Waste percentage
- Commitment coverage

## See Also
- **aws-well-architected** — AWS cost optimization pillar
- **azure-well-architected** — Azure cost optimization pillar
- **gitops-principles** — Infrastructure management
- **dora-metrics** — Delivery metrics include cost
