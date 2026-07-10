---
name: swebok
load-when: Understanding software engineering practices, reviewing process maturity, defining team practices
skip-when: Specific practices (see craftsmanship, testing, devops), architecture decisions (see architecture-decision-records)
---

# SWEBOK (Software Engineering Body of Knowledge)

## Quick Reference
- IEEE标准, 30+ knowledge areas covering all of software engineering
- Key areas: requirements, design, construction, testing, maintenance, configuration management, quality, process, models, tools
- Use as a checklist for team maturity assessment
- Maps to ISTQB, PMBOK, and other standards

## Deep Dive

### Knowledge Areas (Key)
| Area | Description | Atlas Roles |
|------|-------------|-------------|
| Requirements | Elicitation, analysis, specification, validation | atlas-ba, atlas-pm |
| Design | Architectural, detailed, UI/UX design | atlas-architect, atlas-ux |
| Construction | Programming, verification, reuse | atlas-dev |
| Testing | Test levels, techniques, process | atlas-qa |
| Maintenance | Corrective, adaptive, perfective, preventive | atlas-maintenance |
| Configuration Mgmt | Version control, build, release, deployment | atlas-devops |
| Quality | Quality fundamentals, processes, practical considerations | atlas-qa, atlas-reviewer |
| Process | Process implementation, life cycle models, process improvement | atlas-lead, atlas-delivery |

### Process Areas
- **Engineering**: requirements → design → construction → testing → maintenance
- **Supporting**: configuration management, quality assurance, documentation
- **Managing**: project planning, measurement, risk management

### Maturity Assessment
Use SWEBOK to assess team maturity:
1. Identify which knowledge areas the team practices formally
2. Rate maturity: ad hoc → repeatable → defined → managed → optimized
3. Target improvements in highest-impact areas

### Relationship to Other Standards
- ISTQB: testing knowledge area
- PMBOK: project management knowledge area
- OWASP: security practices within design and construction
- CMMI: process maturity model that complements SWEBOK

## See Also
- **swebok** — (this file) — overview of software engineering knowledge areas
- **architecture-decision-records** — Documenting design decisions
- **quality-gates** — Quality assurance checkpoints
- **scrum-guide** — Process implementation
