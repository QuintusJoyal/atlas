---
name: lead-routing
category: knowledge
load-when: Classifying user intent, selecting roles, routing tasks to specialists
skip-when: Individual specialist execution, no routing needed
description: Routing intelligence for atlas-lead — intent classification, keyword mapping, workflow-phase routing, multi-role delegation, artifact ownership, specialist engagement.
audience: [atlas-lead]
tags: [routing, delegation, orchestration]
---

# Routing intelligence

Reference for atlas-lead when classifying intent, matching keywords, and routing to specialist roles. Read this file to select the right role(s) for a task.

## Quick Reference
- Classify intent first: Build/Fix/Review/Test/Design/Deploy/Security/Document/Data/Infra
- Match most-specific keyword first, then add secondary role if needed
- Feature pipeline: pm → architect → dev → qa → reviewer → devops
- Bugfix pipeline: maintenance → dev → qa → reviewer → devops
- Parallel when independent: architect+ux, security+compliance, dev+docs
- Sequential when dependent: pm→architect, architect→dev, dev→qa
- Consult trust profiles before tier allocation (ARTS)

## Intent classification

When the user gives you a task, classify the **intent** first:

| Intent | Signal Words | Primary Role | Secondary | Workflow |
|--------|--------------|--------------|-----------|----------|
| Build | implement, create, add, build, develop, write, make | atlas-dev | atlas-qa | feature |
| Fix | fix, bug, error, issue, regression, broken, crash | atlas-dev + atlas-maintenance | atlas-qa | bugfix |
| Review | review, audit, check, verify, validate, inspect | atlas-reviewer | atlas-security | - |
| Test | test, coverage, test plan, QA, smoke, regression | atlas-qa | atlas-dev | feature |
| Design | design, architect, ADR, NFR, structure, trade-off | atlas-architect | atlas-ux | feature |
| Deploy | deploy, release, ship, push, go live, CI/CD | atlas-devops | atlas-maintenance | feature |
| Security | security, vulnerability, auth, secrets, OWASP | atlas-security | atlas-compliance | security-audit |
| Document | document, README, changelog, runbook, docs | atlas-docs | - | feature |
| Data pipeline | pipeline, ETL, warehousing, streaming, data flow | atlas-data-eng | atlas-dba | data-project |
| Analytics | metrics, dashboard, SQL, BI, report, KPI | atlas-data-analyst | atlas-data-sci | data-project |
| ML model | model, ML, training, evaluation, fairness, MLOps | atlas-data-sci | atlas-ai-eng | data-project |
| AI/LLM | RAG, agent, prompt, LLM, AI, embedding | atlas-ai-eng | atlas-data-sci | feature |
| Infrastructure | server, OS, VM, hardening, hybrid, on-prem | atlas-sysinfra | atlas-network | infra-change |
| Cloud | AWS, Azure, GCP, landing zone, FinOps, cloud | atlas-cloud | atlas-ent-arch | infra-change |
| Network | firewall, VPN, DNS, zero-trust, VPC, subnet | atlas-network | atlas-cloud | infra-change |
| Database | schema, index, query, backup, HA, DR, SQL | atlas-dba | atlas-data-eng | data-project |
| Compliance | GDPR, SOC2, ISO27001, privacy, governance, HIPAA | atlas-compliance | atlas-security | security-audit |

## Trust-based routing

Before delegating, atlas-lead consults role trust profiles (`knowledge/role-trust-profiles.md`):

### Tier allocation
1. Look up role's trust score in `trust-profiles.json`
2. Map score to tier: UNTRUSTED→premium, PROBATION→premium(prefer), STANDARD→standard, TRUSTED→fast
3. Override if task is on critical path or user requests specific tier
4. Log tier selection in team.json

### Trust-informed delegation
- **TRUSTED roles:** can handle parallel tasks, critical path, complex work
- **STANDARD roles:** normal delegation, standard tier
- **PROBATION roles:** assign simpler tasks, premium tier, closer monitoring
- **UNTRUSTED roles:** only simple tasks, premium tier, mandatory review

### Trust updates
After each task, trust scores update based on quality scores and critic pass rates. See `knowledge/role-trust-profiles.md` for the full scoring formula.
| Enterprise | integration, capability, domain, TOGAF, strategy | atlas-ent-arch | atlas-consultant | discovery |
| Planning | timeline, milestone, RAID, risk, stakeholder | atlas-delivery | atlas-pm | feature |
| Discovery | research, explore, spike, POC, investigate | atlas-consultant | atlas-architect | discovery |
| UX | wireframe, user flow, accessibility, UI, design token | atlas-ux | atlas-pm | feature |
| Requirements | stories, acceptance criteria, backlog, PRD, INVEST | atlas-pm | atlas-ba | feature |
| Analysis | edge case, BDD, data flow, process flow, UML | atlas-ba | atlas-pm | feature |
| Incident | incident, outage, P0, oncall, production down | atlas-maintenance | atlas-devops | hotfix |
| Tech debt | refactor, cleanup, modernize, legacy, deprecate | atlas-dev | atlas-architect | feature |

## Keyword-to-role mapping

Match the **most specific** keyword first.

| Keywords | Primary Role | When to Add Secondary |
|----------|--------------|----------------------|
| `implement`, `code`, `function`, `API`, `endpoint`, `feature`, `module` | atlas-dev | Add atlas-qa for tests |
| `bug`, `fix`, `error`, `crash`, `regression`, `failing`, `broken` | atlas-dev | Add atlas-maintenance for triage |
| `review`, `PR`, `merge request`, `diff`, `code review`, `LGTM` | atlas-reviewer | Add atlas-security for sensitive code |
| `test`, `coverage`, `test plan`, `smoke`, `regression test`, `unit test` | atlas-qa | Add atlas-dev for test implementation |
| `design`, `architecture`, `ADR`, `NFR`, `trade-off`, `component` | atlas-architect | Add atlas-ux if UI involved |
| `deploy`, `release`, `pipeline`, `CI/CD`, `rollback`, `canary` | atlas-devops | Add atlas-security for gated deploys |
| `security`, `vulnerability`, `threat`, `OWASP`, `auth`, `token` | atlas-security | Add atlas-compliance if regulated |
| `document`, `README`, `changelog`, `runbook`, `api doc` | atlas-docs | - |
| `pipeline`, `ETL`, `warehousing`, `streaming`, `ingestion` | atlas-data-eng | Add atlas-dba for schema |
| `metrics`, `dashboard`, `SQL`, `BI`, `report`, `KPI` | atlas-data-analyst | Add atlas-data-sci for ML metrics |
| `model`, `ML`, `training`, `evaluation`, `fairness`, `MLOps` | atlas-data-sci | Add atlas-ai-eng for MLOps |
| `RAG`, `LLM`, `agent`, `prompt`, `embedding`, `vector` | atlas-ai-eng | Add atlas-data-sci for data prep |
| `server`, `OS`, `VM`, `hardening`, `hybrid`, `on-prem` | atlas-sysinfra | Add atlas-network for connectivity |
| `AWS`, `Azure`, `GCP`, `cloud`, `FinOps`, `landing zone` | atlas-cloud | Add atlas-ent-arch for strategy |
| `firewall`, `VPN`, `DNS`, `VPC`, `zero-trust`, `subnet` | atlas-network | Add atlas-cloud for cloud networking |
| `schema`, `index`, `query`, `backup`, `HA`, `replication` | atlas-dba | Add atlas-data-eng for pipelines |
| `GDPR`, `SOC2`, `ISO27001`, `privacy`, `HIPAA` | atlas-compliance | Add atlas-security for technical controls |
| `integration`, `capability`, `domain`, `TOGAF`, `strategy` | atlas-ent-arch | Add atlas-consultant for client work |
| `timeline`, `milestone`, `RAID`, `risk`, `stakeholder` | atlas-delivery | Add atlas-pm for requirements |
| `research`, `explore`, `spike`, `POC`, `investigate` | atlas-consultant | Add atlas-architect for feasibility |
| `wireframe`, `user flow`, `accessibility`, `UI`, `WCAG` | atlas-ux | Add atlas-pm for requirements |
| `stories`, `acceptance criteria`, `backlog`, `PRD`, `INVEST` | atlas-pm | Add atlas-ba for analysis |
| `edge case`, `BDD`, `data flow`, `process flow`, `UML` | atlas-ba | Add atlas-pm for prioritization |
| `incident`, `outage`, `P0`, `oncall`, `production down` | atlas-maintenance | Add atlas-devops for remediation |
| `refactor`, `cleanup`, `modernize`, `legacy`, `deprecate` | atlas-dev | Add atlas-architect for design |

## Workflow-phase routing

Each workflow has active phases. Route based on current phase:

| Workflow | Phase | Active Roles | Lead Routes To |
|----------|-------|--------------|----------------|
| **feature** | Requirements | atlas-pm, atlas-ba | atlas-pm first, then atlas-ba |
| **feature** | Design | atlas-architect, atlas-ux | atlas-architect + atlas-ux (parallel) |
| **feature** | Implementation | atlas-dev, atlas-docs | atlas-dev (+ atlas-docs in parallel) |
| **feature** | Testing | atlas-qa | atlas-qa |
| **feature** | Review | atlas-reviewer, atlas-security | atlas-reviewer + atlas-security (parallel) |
| **feature** | Deploy | atlas-devops | atlas-devops |
| **feature** | Maintenance | atlas-maintenance | atlas-maintenance |
| **bugfix** | Triage | atlas-maintenance | atlas-maintenance |
| **bugfix** | Fix | atlas-dev | atlas-dev |
| **bugfix** | Test | atlas-qa | atlas-qa |
| **bugfix** | Review | atlas-reviewer | atlas-reviewer |
| **bugfix** | Deploy | atlas-devops | atlas-devops |
| **data-project** | Requirements | atlas-pm, atlas-ba | atlas-pm |
| **data-project** | Design | atlas-data-eng, atlas-dba, atlas-architect | atlas-data-eng + atlas-dba + atlas-architect |
| **data-project** | Build | atlas-data-eng, atlas-data-sci | atlas-data-eng + atlas-data-sci |
| **data-project** | Validate | atlas-data-analyst, atlas-qa | atlas-data-analyst + atlas-qa |
| **data-project** | Deploy | atlas-devops | atlas-devops |
| **infra-change** | Requirements | atlas-pm, atlas-delivery | atlas-pm or atlas-delivery |
| **infra-change** | Design | atlas-cloud, atlas-sysinfra, atlas-network, atlas-ent-arch | atlas-cloud + atlas-sysinfra + atlas-network |
| **infra-change** | Implement | atlas-devops, atlas-sysinfra, atlas-network | atlas-devops + atlas-sysinfra |
| **infra-change** | Security | atlas-security, atlas-compliance | atlas-security + atlas-compliance |
| **infra-change** | Deploy | atlas-devops | atlas-devops |
| **security-audit** | Scope | atlas-pm, atlas-consultant | atlas-pm or atlas-consultant |
| **security-audit** | Audit | atlas-security | atlas-security |
| **security-audit** | Review | atlas-reviewer | atlas-reviewer |
| **security-audit** | Compliance | atlas-compliance | atlas-compliance |
| **security-audit** | Report | atlas-docs | atlas-docs |
| **discovery** | Research | atlas-consultant, atlas-pm, atlas-ba | atlas-consultant |
| **discovery** | Feasibility | atlas-architect or atlas-ent-arch, atlas-cloud | atlas-architect |
| **discovery** | Proposal | atlas-consultant | atlas-consultant |

## Multi-role delegation rules

**Parallel delegation** — delegate to multiple roles simultaneously when:

| Scenario | Parallel Roles | Why |
|----------|----------------|-----|
| Feature with UI | atlas-architect + atlas-ux | Design and UX are independent |
| Implementation + docs | atlas-dev + atlas-docs | Code and docs can be written simultaneously |
| Security + compliance gate | atlas-security + atlas-compliance | Both review independently |
| Data project design | atlas-data-eng + atlas-dba + atlas-data-sci | Different data concerns |
| Infra design | atlas-cloud + atlas-sysinfra + atlas-network | Different infrastructure layers |
| Code + test design | atlas-dev + atlas-qa | Test design can start with spec |
| Audit + review | atlas-security + atlas-reviewer | Independent quality checks |
| PM + BA requirements | atlas-pm + atlas-ba | Joint requirements ownership |

**Sequential delegation** — chain roles in order when:

| Scenario | Sequence | Why |
|----------|----------|-----|
| Requirements → Design | atlas-pm → atlas-architect | Design needs requirements |
| Design → Implementation | atlas-architect → atlas-dev | Code needs design |
| Implementation → Test | atlas-dev → atlas-qa | Tests need code |
| Test → Review | atlas-qa → atlas-reviewer | Review needs tests |
| Review → Deploy | atlas-reviewer → atlas-devops | Deploy needs approval |
| Triage → Fix | atlas-maintenance → atlas-dev | Fix needs root cause |
| Scope → Audit | atlas-consultant → atlas-security | Audit needs scope |

## Artifact ownership

| Artifact | Owner | Reviewer | Gate |
|----------|-------|----------|------|
| requirements.md | atlas-pm | atlas-ba | Gate 1 |
| design.md | atlas-architect | atlas-reviewer | Gate 2 |
| code/* | atlas-dev | atlas-reviewer | Gate 3 |
| test-plan.md | atlas-qa | atlas-reviewer | Gate 3 |
| security.md | atlas-security | atlas-compliance | Gate 3 |
| pipeline.yml | atlas-devops | atlas-security | Gate 3 |
| README.md | atlas-docs | atlas-reviewer | Gate 3 |
| team.json | atlas-lead | - | - |
| budget.md | atlas-lead | - | - |
| decisions.md | atlas-lead | - | - |

## On-demand specialist engagement

Enterprise specialists are engaged when the domain calls for them:

| Domain | Specialist | Trigger |
|--------|------------|---------|
| Cloud architecture | atlas-cloud | AWS, Azure, GCP, landing zones, FinOps |
| Network security | atlas-network | Firewall, VPN, DNS, zero-trust, VPC |
| Systems infrastructure | atlas-sysinfra | Server, OS, VM, hardening, hybrid |
| Database | atlas-dba | Schema, index, query, backup, HA |
| Data engineering | atlas-data-eng | Pipeline, ETL, warehousing, streaming |
| Data science | atlas-data-sci | ML model, training, evaluation, fairness |
| AI/LLM | atlas-ai-eng | RAG, agent, prompt, LLM, embedding |
| Data analysis | atlas-data-analyst | Metrics, dashboard, SQL, BI |
| Enterprise architecture | atlas-ent-arch | Integration, capability, domain, TOGAF |
| Delivery management | atlas-delivery | Timeline, milestone, RAID, risk |
| Consulting | atlas-consultant | Discovery, research, POC, client work |
| Compliance | atlas-compliance | GDPR, SOC2, ISO27001, privacy |
