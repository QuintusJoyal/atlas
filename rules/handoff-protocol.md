---
name: handoff-protocol
description: Structured handoff artifact format that roles exchange during the pipeline. Load during pipeline handoffs and escalations.
load: on-demand
---

# Handoff protocol

When a role finishes a pipeline step, it returns a structured artifact so the **next role, atlas-lead, or the user** can pick it up cleanly. **Assume the reader has no chat history and may not know the project.** Write in plain language; cite file paths; state decisions explicitly.

Keep the body concise, but never omit context the next actor needs to act.

```
## Role: <role name>
## Workflow: <preset> | Run: <run-id>
## Variant: <small|full>
## Phase state: <pending|active|gated|completed|failed|paused|aborted>

### Inputs
What this role received: prior artifact **paths**, user decisions, constraints, and relevant code locations. Enough detail that someone who did not run the prior step can understand the starting point.

### Work done
A short summary of what was produced or decided. Name key files changed or created (paths).

### Outputs
Concrete deliverables (files, links, decisions). Reference paths, do not paste large content. If the next role should read specific files first, list them in order.

### Open questions
Anything unresolved. Mark items needing the user with [USER]. Route requirement gaps to atlas-pm or atlas-ba. Do not leave implicit assumptions.

### Resource requests
Resources needed from the user or a peer, each with a one-line justification.

### Token budget
**Required** for every handoff. State your phase estimate: **light**, **medium**, or **heavy**, plus one-line rationale (files, complexity, premium-tier use). If downgraded, note tier change. Flag premium gate downgrades.

### Definition of Done
Checklist for this step, each item checked or flagged.

### Next role
Who should pick this up, **why**, and what they should do first (concrete next action, not "continue the work").
```

### Small variant template

For small variants, use this compressed template (4 sections instead of 8):

```
## Role: <role name>
## Run: <run-id> | Variant: small

### Summary
What was done. Key files changed.

### Outputs
Files created/modified. Decisions made.

### Issues
Blockers, questions, or risks.

### Next
Who picks up next and what they do first.
```

Small variant handoffs skip: Inputs, Resource requests, Token budget, Definition of Done. The DoD is implicit (role completed = gate passed).

Persist the artifact in the central run workspace at `$ATLAS_DATA_DIR/runs/<run-id>/` (for example `requirements.md`, `design.md`, `test-plan.md`, `review.md`, `decisions.md`, `budget.md`). These are local files, not MCP writes. **Do not** create `.atlas/` or run trees in project repos.

## Handoff contracts

Each role has a defined input/output contract. A handoff is incomplete if any required field is missing. atlas-lead validates handoffs before passing them to the next role.

### Contract table

| Role | Required Inputs | Required Outputs |
|------|----------------|-----------------|
| atlas-pm | User goal or feature request | requirements.md (user stories, acceptance criteria, MoSCoW, scope) |
| atlas-ba | requirements.md from atlas-pm | refined-requirements.md (edge cases, BDD scenarios, data flows) |
| atlas-architect | requirements.md, refined-requirements.md | design.md (C4 diagrams, ADRs, NFRs, trade-offs) |
| atlas-dev | design.md, API contracts | implementation summary (files changed, approach, test results) |
| atlas-qa | implementation summary, acceptance criteria | test-plan.md (test results, coverage, bug reports) |
| atlas-security | design.md or implementation diff | security-assessment.md (findings by severity, gate verdict) |
| atlas-reviewer | implementation diff, test results, security findings | review.md (verdict, findings by severity) |
| atlas-devops | merge approval, security clearance | deployment artifact (pipeline, IaC, rollback plan) |
| atlas-docs | implementation details, architecture context | documentation artifact (README, changelog, runbook) |
| atlas-compliance | security-assessment.md, scope | compliance-report.md (findings, control gaps, pass/block) |
| atlas-ux | user stories, edge cases | wireframes + design tokens + user flows |
| atlas-db | data requirements, access patterns | database-schema.md (DDL, indexing, migration scripts) |
| atlas-data-eng | source schemas, warehouse target | pipeline architecture (DAG, data contracts, quality specs) |
| atlas-data-sci | curated datasets, feature store | model-results.md (evaluation, model card, fairness audit) |
| atlas-data-analyst | data-pipeline-spec.md, business question | kpi-report.md (metrics, trends, SQL, visualizations) |
| atlas-ai-eng | system-design.md, integration points | ai-component-spec.md (RAG/agent design, eval criteria) |
| atlas-cloud | architecture decisions, requirements | cloud-architecture.md (diagram, cost estimate, security) |
| atlas-network | cloud architecture, security requirements | network-topology.md (diagram, firewall rules, VPN) |
| atlas-sysinfra | network topology, OS requirements | server-inventory.md (hardening report, VM templates) |
| atlas-ent-arch | business context, constraints | enterprise-architecture.md (capability map, integration patterns) |
| atlas-consultant | client context, objectives | engagement-scope.md (problem framing, proposal) |
| atlas-delivery | project scope, milestones | delivery-status.md (RAID, timeline, status) |
| atlas-maintenance | incident details, logs | triage summary (root cause, fix recommendation, postmortem) |
| atlas-ux | user stories, edge cases | wireframes + design tokens + user flows |

### Input contract format

When a role receives a handoff, it expects:
- **Artifact paths:** specific files to read (not the full content pasted into the brief)
- **User decisions:** any explicit choices the user has made
- **Constraints:** budget, timeline, technology, or regulatory constraints
- **Open questions:** anything the prior role couldn't resolve

### Output contract format

When a role produces a handoff, it must include:
- **Artifact paths:** files created or modified (absolute paths in the run workspace)
- **Decisions made:** what was chosen and why
- **Next action:** what the next role should do first (concrete, not "continue the work")
- **Token budget:** light / medium / heavy with one-line rationale

### Team manifest
Update `$ATLAS_DATA_DIR/runs/<run-id>/team.json` for your role: set your entry to `completed` or `failed`, add a short `note`, and set `completedAt`. If you ran on a downgraded tier, set `model` and `downgradedFrom` when atlas-lead re-delegated after a quota interrupt. If no entry exists, atlas-lead should have seeded the file; add your row if missing. See `knowledge/collaboration.md`.

## State transitions

When a role returns a handoff, atlas-lead updates the phase state in `team.json`:

| Handoff result | State transition | Lead action |
| --- | --- | --- |
| Success with complete DoD | active → gated | Update team.json, present to user for gate approval |
| Success with partial DoD | active → active | Note gaps, re-delegate to same role to complete |
| Failure (role failed) | active → failed | Log failure, attempt resilience cascade (re-delegate at lower tier) |
| Scope change detected | active → paused | Pause phase, delegate re-evaluation to PM/BA |
| User aborts | any → aborted | Set all pending/active phases to aborted, update budget.md |

### Gate approval flow
1. Role returns handoff → state becomes `gated`
2. Lead validates handoff completeness (all required fields present)
3. Lead checks DoD checklist items
4. Lead presents to user for approval
5. User approves → state becomes `completed`
6. User rejects → state becomes `failed`, lead re-delegates with feedback

### Scope change flow
1. Scope change detected during active phase → state becomes `paused`
2. Lead delegates re-evaluation to atlas-pm or atlas-ba
3. PM/BA returns impact assessment
4. Lead presents options to user: resume, restart from phase X, abort, switch variant
5. User decides → lead executes (resume → active, restart → reset phases, abort → aborted)
