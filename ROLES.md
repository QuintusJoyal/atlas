# Atlas roles

Invoke any role directly with `/atlas-<role>` for a consultative session, or let `/atlas-lead` orchestrate them. Premium roles use deeper reasoning and are rationed; standard and fast roles handle everyday and high-volume work.

## Orchestrator
| Role | When to use | Example |
|------|-------------|---------|
| atlas-lead | Run a task across the team end to end, manage gates, pull in specialists | `/atlas-lead take the export feature from requirements to deploy-ready` |

## Core SDLC roles
| Role | When to use | Example |
|------|-------------|---------|
| atlas-pm | Requirements, user stories, acceptance criteria, backlog | `/atlas-pm draft stories for CSV export` |
| atlas-ba | Analysis, edge cases, BDD scenarios, data flows | `/atlas-ba map edge cases for the refund flow` |
| atlas-architect | System design, ADRs, NFRs, trade-offs | `/atlas-architect propose a design for the notifications service` |
| atlas-ux | User flows, accessibility, wireframes, design tokens | `/atlas-ux design the onboarding flow` |
| atlas-dev | Implementation against a plan | `/atlas-dev implement the export endpoint` |
| atlas-qa | Test plans, automated tests, bug reports | `/atlas-qa write tests for the export endpoint` |
| atlas-security | Security audit, threat model, secrets scan; deploy gate | `/atlas-security audit the auth module` |
| atlas-reviewer | Code review, charter conformance, human-voice check | `/atlas-reviewer review the open changes` |
| atlas-devops | CI/CD, IaC, release and rollback, observability | `/atlas-devops set up the deploy pipeline` |
| atlas-maintenance | Triage, debugging, regressions, tech-debt, postmortems | `/atlas-maintenance investigate the latency regression` |
| atlas-docs | README, changelog, runbooks, user docs | `/atlas-docs document the export feature` |

## Enterprise specialists (engaged on demand)
| Role | When to use | Example |
|------|-------------|---------|
| atlas-network | Topology, segmentation, firewalls, VPN, DNS, zero-trust | `/atlas-network review the VPC segmentation` |
| atlas-sysinfra | OS and server hardening, virtualization, on-prem and hybrid | `/atlas-sysinfra harden the bastion host` |
| atlas-cloud | Cloud architecture, landing zones, FinOps | `/atlas-cloud design the multi-account landing zone` |
| atlas-dba | Schema, indexing and tuning, backup, HA and DR | `/atlas-dba tune the slow reporting queries` |
| atlas-data-eng | Pipelines, ETL and ELT, warehousing, streaming | `/atlas-data-eng design the ingestion pipeline` |
| atlas-data-sci | Modeling, evaluation, MLOps | `/atlas-data-sci propose a churn model and evaluation plan` |
| atlas-ai-eng | RAG, agents, prompts and evals, guardrails; also team optimizer | `/atlas-ai-eng optimize the team` |
| atlas-data-analyst | Metrics, dashboards, SQL analytics | `/atlas-data-analyst build the weekly KPI dashboard` |
| atlas-ent-arch | Cross-system strategy, integration, capability mapping | `/atlas-ent-arch map the integration between billing and CRM` |
| atlas-delivery | Planning, RAID and risk, stakeholder management | `/atlas-delivery build a delivery plan for Q3` |
| atlas-consultant | Discovery, proposals and SOWs, client communication | `/atlas-consultant run discovery for the new engagement` |
| atlas-compliance | GDPR, SOC 2, ISO 27001, data governance, privacy | `/atlas-compliance assess the data retention policy` |

## Workflow presets
`atlas-lead` selects a preset from `workflows/`: feature, bugfix, data-project, infra-change, security-audit, discovery. You can override the choice.
