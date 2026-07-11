# Atlas roles

Invoke any role directly with `atlas-<role>` for a consultative session, or let `atlas-lead` orchestrate them. Premium roles use deeper reasoning and are rationed; standard and fast roles handle everyday and high-volume work.

## Orchestrator

| Role | When to use | Key trait | Example |
|------|-------------|-----------|---------|
| atlas-lead | Run a task across the team end to end, manage gates, pull in specialists | Router, not doer | `atlas-lead take the export feature from requirements to deploy-ready` |

---

## Core SDLC roles

| Role | When to use | Key trait | Example |
|------|-------------|-----------|---------|
| atlas-pm | Requirements, user stories, acceptance criteria, backlog | Defines **what** and **why** | `atlas-pm draft stories for CSV export` |
| atlas-ba | Analysis, edge cases, BDD scenarios, data flows | Finds **edge cases** others miss | `atlas-ba map edge cases for the refund flow` |
| atlas-architect | System design, ADRs, NFRs, trade-offs | Designs **simple** systems that scale | `atlas-architect propose a design for the notifications service` |
| atlas-ux | User flows, accessibility, wireframes, design tokens | Designs for **humans** first | `atlas-ux design the onboarding flow` |
| atlas-dev | Implementation against a plan | Writes **correct, tested** code | `atlas-dev implement the export endpoint` |
| atlas-qa | Test plans, automated tests, bug reports | **Proves** work meets criteria | `atlas-qa write tests for the export endpoint` |
| atlas-security | Security audit, threat model, secrets scan; deploy gate | **Gate** before deploy | `atlas-security audit the auth module` |
| atlas-reviewer | Code review, charter conformance, human-voice check | **Quality** and consistency | `atlas-reviewer review the open changes` |
| atlas-devops | CI/CD, IaC, release and rollback, observability | Ships **safely** | `atlas-devops set up the deploy pipeline` |
| atlas-maintenance | Triage, debugging, regressions, tech-debt, postmortems | Keeps **production** healthy | `atlas-maintenance investigate the latency regression` |
| atlas-docs | README, changelog, runbooks, user docs | Communicates **clearly** | `atlas-docs document the export feature` |

---

## Enterprise specialists (engaged on demand)

| Role | When to use | Key trait | Example |
|------|-------------|-----------|---------|
| atlas-network | Topology, segmentation, firewalls, VPN, DNS, zero-trust | **Secures** the network | `atlas-network review the VPC segmentation` |
| atlas-sysinfra | OS and server hardening, virtualization, on-prem and hybrid | **Hardens** infrastructure | `atlas-sysinfra harden the bastion host` |
| atlas-cloud | Cloud architecture, landing zones, FinOps | **Designs** cloud at scale | `atlas-cloud design the multi-account landing zone` |
| atlas-dba | Schema, indexing and tuning, backup, HA and DR | **Optimizes** data stores | `atlas-dba tune the slow reporting queries` |
| atlas-data-eng | Pipelines, ETL and ELT, warehousing, streaming | **Moves** data reliably | `atlas-data-eng design the ingestion pipeline` |
| atlas-data-sci | Modeling, evaluation, MLOps | **Builds** ML with rigor | `atlas-data-sci propose a churn model and evaluation plan` |
| atlas-ai-eng | RAG, agents, prompts and evals, guardrails; also team optimizer | **Builds** AI safely | `atlas-ai-eng optimize the team` |
| atlas-data-analyst | Metrics, dashboards, SQL analytics | **Turns** data into insight | `atlas-data-analyst build the weekly KPI dashboard` |
| atlas-ent-arch | Cross-system strategy, integration, capability mapping | **Designs** enterprise scale | `atlas-ent-arch map the integration between billing and CRM` |
| atlas-delivery | Planning, RAID and risk, stakeholder management | **Keeps** projects on track | `atlas-delivery build a delivery plan for Q3` |
| atlas-consultant | Discovery, proposals and SOWs, client communication | **Frames** problems | `atlas-consultant run discovery for the new engagement` |
| atlas-compliance | GDPR, SOC 2, ISO 27001, data governance, privacy | **Ensures** compliance | `atlas-compliance assess the data retention policy` |

---

## Role boundaries (who does what)

| Domain | Primary owner | Secondary |
|--------|---------------|-----------|
| User stories & requirements | atlas-pm | atlas-ba |
| Edge cases & BDD | atlas-ba | atlas-pm |
| System design & ADRs | atlas-architect | atlas-ent-arch |
| UX & accessibility | atlas-ux | atlas-pm |
| Implementation code | atlas-dev | - |
| Tests & QA | atlas-qa | atlas-dev |
| Security audits | atlas-security | atlas-compliance |
| Code review | atlas-reviewer | atlas-security |
| CI/CD & deployment | atlas-devops | atlas-maintenance |
| Incident response | atlas-maintenance | atlas-devops |
| Documentation | atlas-docs | atlas-architect |
| Cloud architecture | atlas-cloud | atlas-ent-arch |
| Network design | atlas-network | atlas-cloud |
| Server hardening | atlas-sysinfra | atlas-network |
| Database design & tuning | atlas-dba | atlas-data-eng |
| Data pipelines | atlas-data-eng | atlas-dba |
| ML modeling | atlas-data-sci | atlas-ai-eng |
| AI/LLM systems | atlas-ai-eng | atlas-data-sci |
| Metrics & BI | atlas-data-analyst | atlas-data-sci |
| Enterprise strategy | atlas-ent-arch | atlas-consultant |
| Project planning | atlas-delivery | atlas-pm |
| Client engagement | atlas-consultant | atlas-delivery |
| Regulatory compliance | atlas-compliance | atlas-security |

---

## Workflow presets

`atlas-lead` selects a preset from `workflows/`: feature, bugfix, data-project, infra-change, security-audit, discovery. You can override the choice.

See `knowledge/context/lead-routing.md` for the exhaustive routing table that maps tasks to the right specialist.
