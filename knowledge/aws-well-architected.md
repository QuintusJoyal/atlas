---
name: aws-well-architected
load-when: Reviewing AWS architecture, cloud design decisions, cost optimization
skip-when: Azure architecture (see azure-well-architected), FinOps (see finops-practices)
---

# AWS Well-Architected Framework

## Quick Reference
- 6 pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability
- Well-Architected Review: structured assessment against pillars
- Use to evaluate and improve cloud architectures
- Each pillar has design principles and best practices
- Free tool: AWS Well-Architected Tool in console

## Deep Dive

### The 6 Pillars
| Pillar | Focus | Key Practices |
|--------|-------|---------------|
| Operational Excellence | Run and monitor systems | Automation, IaC, observability |
| Security | Protect data and systems | Encryption, IAM, detection |
| Reliability | Recover from failures | Fault tolerance, scaling, DR |
| Performance Efficiency | Use resources efficiently | Right-sizing, caching, CDN |
| Cost Optimization | Avoid unnecessary costs | Reserved instances, spot, cleanup |
| Sustainability | Minimize environmental impact | Efficiency, renewable energy |

### Design Principles
1. Stop guessing capacity needs
2. Test at production scale
3. Automate with architectural experimentation in mind
4. Consider evolutionary architectures
5. Drive architectures using data
6. Improve through game days
7. Use managed services when possible

### Well-Architected Review Process
1. Define workload
2. Select lens (general or industry-specific)
3. Answer questions for each pillar
4. Identify improvements
5. Prioritize improvements
6. Track progress

## See Also
- **azure-well-architected** — Azure equivalent
- **finops-practices** — Cost optimization details
- **gitops-principles** — Infrastructure as code
- **cis-benchmarks** — Security configuration
