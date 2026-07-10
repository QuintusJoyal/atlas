---
name: readme
category: reference
description: Atlas knowledge base index — files, workflow, and hygiene rules for the shared team memory.
audience: [atlas-lead, all]
tags: [knowledge-base, index, reference, setup]
---

# Atlas knowledge base

The shared memory of the Atlas team. It ships with the bundle and installs to `$ATLAS_DATA_DIR/knowledge/`. Anyone (human or role) can open and read it directly.

## Shipped vs installed

| Location | Purpose |
| --- | --- |
| Repo `knowledge/` | Source files in version control. Install copies them to `$ATLAS_DATA_DIR/knowledge/`. |
| `$ATLAS_DATA_DIR/knowledge/` | Live KB on your machine. Roles read and write here during work. |

On **update**, install preserves your local edits to `lessons.md`, `proposed.md`, `ways-of-working.md`, and `usage-insights.md`. New bundle files can be merged with `./scripts/merge-knowledge.ps1`.

Canonical Framework docs (`core-values-charter.md`, `enterprise-org-model.md`, `atlas-framework.md`, `retro-template.md`, and others) ship in both places after install.

## Files

- `lessons.md`: canonical, approved lessons. Every role reads this before acting.
- `proposed.md`: a queue of new lessons drafted by roles. The user approves in batches; approved items move to `lessons.md`. **The repo copy includes example entries** that show the format. They are not private data; replace or clear them after install if you prefer a clean queue.
- `ways-of-working.md`: approved process and idea changes, plus a proposed section.
- `usage-insights.md`: atlas-ai-eng logs usage patterns and efficiency recommendations here.
- `branding-values.md`: Atlas name, tagline, core values, visual identity, and voice.

## How it works

1. Before acting, a role reads `lessons.md` (topic-indexed; read only the relevant part).
2. After work, a role appends any new, non-obvious lesson to `proposed.md` with a one-line rationale and source.
3. The user reviews `proposed.md` and `ways-of-working.md` in batches and promotes approved items.

## Knowledge Files (Domain Reference)

Each file is standalone and shareable. Agents search via playbook Knowledge Index; humans read directly.

### Testing
| File | Topic | Used By |
|------|-------|---------|
| testing-pyramid.md | Unit/integration/E2E ratios | qa, dev |
| bdd-gherkin.md | Given/When/Then, feature files | qa, ba |
| istqb-test-levels.md | ISTQB test classification | qa |
| risk-based-testing.md | Risk assessment, prioritization | qa |
| test-design-techniques.md | Equivalence partitioning, boundaries | qa |

### Security
| File | Topic | Used By |
|------|-------|---------|
| owasp-asvs.md | Security verification controls | security, compliance |
| owasp-top-10.md | Top web vulnerabilities | security, dev |
| stride-threat-modeling.md | Threat identification | security, architect |
| nist-800-53-controls.md | Security control families | security, compliance |
| cwe-sans-top-25.md | Most dangerous weaknesses | security, dev |

### Architecture
| File | Topic | Used By |
|------|-------|---------|
| c4-model.md | Architecture diagrams | architect, ent-arch |
| architecture-decision-records.md | ADR format | architect |
| domain-driven-design.md | Bounded contexts, aggregates | architect, ent-arch |
| swebok.md | Software engineering body of knowledge | architect, dev |
| trade-off-analysis.md | Decision matrices | architect, ent-arch |

### DevOps
| File | Topic | Used By |
|------|-------|---------|
| google-sre-practices.md | SLO/SLI, error budgets | devops, maintenance |
| dora-metrics.md | Delivery performance metrics | devops |
| gitops-principles.md | Git as source of truth | devops |
| itil-incident-management.md | Incident lifecycle | maintenance, devops |

### Data
| File | Topic | Used By |
|------|-------|---------|
| kimball-dimensional-modeling.md | Star schema, SCDs | dba, data-eng |
| dbt-best-practices.md | Staging/intermediate/marts | data-eng |
| apache-airflow-patterns.md | DAGs, operators, sensors | data-eng |
| great-expectations.md | Data quality validation | data-eng, data-analyst |
| crisp-dm.md | Data science methodology | data-sci |

### Software Craftsmanship
| File | Topic | Used By |
|------|-------|---------|
| solid-principles.md | SRP, OCP, LSP, ISP, DIP | dev, reviewer |
| clean-code-practices.md | Naming, functions, formatting | dev, reviewer |
| test-driven-development.md | Red-green-refactor | dev, qa |
| refactoring-patterns.md | Code smells, refactoring | dev |
| conventional-commits.md | Commit format, types | dev |

### Project Delivery
| File | Topic | Used By |
|------|-------|---------|
| pmbok-framework.md | Process groups, knowledge areas | delivery, lead |
| babok-techniques.md | Requirements elicitation | ba, pm |
| scrum-guide.md | Roles, events, artifacts | lead, delivery |
| raid-log-management.md | Risks, assumptions, issues, dependencies | delivery, lead |
| raci-matrix.md | Role assignment | delivery, lead |

### Compliance
| File | Topic | Used By |
|------|-------|---------|
| gdpr-requirements.md | Data subject rights, DPIA | compliance |
| soc2-controls.md | Trust service criteria | compliance |
| iso-27001-annex-a.md | ISMS controls | compliance |
| nist-csf.md | Cybersecurity framework | compliance |

### AI/ML
| File | Topic | Used By |
|------|-------|---------|
| nist-ai-rmf.md | AI risk management | ai-eng, data-sci |
| owasp-llm-top-10.md | LLM vulnerabilities | ai-eng |
| anthropic-context-engineering.md | Context windows, progressive disclosure | ai-eng |
| model-cards.md | Model documentation | ai-eng, data-sci |

### UX
| File | Topic | Used By |
|------|-------|---------|
| wcag-2-1-checklist.md | Accessibility requirements | ux |
| nielsen-heuristics.md | 10 usability heuristics | ux |
| material-design-principles.md | Layout, color, typography | ux |

### Cloud/Infrastructure
| File | Topic | Used By |
|------|-------|---------|
| aws-well-architected.md | 6 pillars, best practices | cloud, devops |
| azure-well-architected.md | 5 pillars, optimization | cloud |
| finops-practices.md | Cost optimization | cloud |
| cis-benchmarks.md | Security configuration baselines | sysinfra, security |

### Decision Frameworks
| File | Topic | Used By |
|------|-------|---------|
| mece-framework.md | Mutually exclusive, collectively exhaustive | consultant, ba |
| socratic-method.md | Structured questioning | consultant, ba |
| spin-selling.md | Situation/problem/implication/need-payoff | consultant, ba |
| minto-pyramid.md | Structured communication | consultant, delivery |
| 5-whys-root-cause.md | Iterative root cause analysis | maintenance |

### Quality
| File | Topic | Used By |
|------|-------|---------|
| definition-of-done.md | DoD checklist | qa, reviewer, pm |
| review-checklists.md | Code/design review criteria | reviewer |
| quality-gates.md | Phase transition criteria | reviewer, lead |

### Anti-Patterns
| File | Topic | Used By |
|------|-------|---------|
| anti-patterns.md | Deployment, architecture, testing, data failure patterns | all |

## Hygiene

- Never store secrets, credentials, or PII here.
- Keep `lessons.md` lean and topic-indexed. Curate and merge as it grows.
- atlas-ai-eng periodically proposes pruning stale or superseded lessons.
- Knowledge files are standalone. Each file works without loading others.
- When adding new knowledge files, update this index and the relevant playbook Knowledge Index.
