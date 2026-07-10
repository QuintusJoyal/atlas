---
name: azure-well-architected
load-when: Reviewing Azure architecture, cloud design decisions, Microsoft cloud best practices
skip-when: AWS architecture (see aws-well-architected), FinOps (see finops-practices)
---

# Azure Well-Architected Framework

## Quick Reference
- 5 pillars: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency
- Azure-specific implementation of cloud best practices
- Well-Architected Review in Azure Advisor
- Use with Azure landing zones for enterprise adoption
- Each pillar has specific Azure services and patterns

## Deep Dive

### The 5 Pillars
| Pillar | Focus | Key Azure Services |
|--------|-------|-------------------|
| Reliability | Fault tolerance, DR | Availability Zones, Traffic Manager, Azure Backup |
| Security | Zero trust, defense in depth | Azure AD, Key Vault, Defender, Sentinel |
| Cost Optimization | Right-sizing, reservations | Cost Management, Reserved VMs, Spot VMs |
| Operational Excellence | IaC, monitoring | Azure Monitor, ARM/Bicep, Azure DevOps |
| Performance Efficiency | Scalability, caching | App Service, Azure Cache, CDN |

### Azure-Specific Patterns
- **Microservices with AKS**: containerized workloads
- **Serverless**: Azure Functions for event-driven
- **Event-driven**: Event Grid, Service Bus
- **Data patterns**: Cosmos DB, Azure SQL, Data Lake

### Azure Landing Zones
Pre-configured environment for enterprise adoption:
- Management groups and subscriptions
- Identity and access management
- Network topology
- Security baseline
- Policy and governance

## See Also
- **aws-well-architected** — AWS equivalent
- **finops-practices** — Cost optimization details
- **gitops-principles** — Infrastructure as code
- **cis-benchmarks** — Security configuration
