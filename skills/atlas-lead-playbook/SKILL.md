---
name: atlas-lead-playbook
description: Orchestration methodology for atlas-lead: workflow selection, delegation, gates, token budget, and conflict resolution. Use when atlas-lead runs a pipeline.
disable-model-invocation: true
---

# Atlas lead playbook

Standards: Scrum facilitation, structured handoffs, risk-based gating. References: [Scrum Guide](https://scrumguides.org/), Atlas team charter and handoff protocol.

## Workflow selection

| Preset | When | Gates |
| --- | --- | --- |
| feature | Net-new work | Requirements, design, final |
| bugfix / hotfix | Defects | Final only |
| data-project | Pipelines, analytics, ML | All three |
| infra-change | CI/CD, cloud, network | Design + final (+ security) |
| security-audit | Audit only | Final (findings) |
| discovery | Scope and proposal | Requirements only |

Unknown shapes fall back to `feature`. The user can override.

## Delegation brief

Each subagent gets a self-contained brief: goal, constraints, prior artifacts (paths in `.atlas/runs/<run-id>/`), workflow name, run id, and expected handoff format. Subagents do not see the chat.

Parallelize independent work (e.g. atlas-ux with atlas-architect, atlas-docs with atlas-dev) when the Task tool allows. If nested delegation is unavailable, run sequentially.

## Token-budget protocol

1. Estimation huddle: ask roles that will do the work for size (files, volume, pipeline length, role count, premium-tier use).
2. atlas-ai-eng aggregates into light, medium, or heavy.
3. Heavy: pause, present estimate and cheaper alternative, wait for user approval.
4. Mid-task overrun: stop, return with cost-cut suggestions, re-approve, resume.
5. Prefer fast tier and reuse over regeneration. Log overruns in `budget.md`.

## Model resilience (automatic downgrade)

The user does not want quota limits to interrupt work. When a step fails on quota, rate limit, unavailability, or a block, downgrade and continue. Do not ask permission to downgrade.

1. Cascade: `claude-opus-4-8-thinking-high` to `composer-2.5` to `composer-2.5-fast` to `inherit`. See `~/.cursor/atlas-knowledge/model-resilience.md`.
2. Transient rate limit: one short retry at the same tier first. If it persists, downgrade.
3. Apply the downgrade only to the affected step. The next step starts at its own assigned tier.
4. Log each downgrade in `budget.md` and `usage-insights.md`: role, from tier, to tier, reason, run id.
5. Inform the user in the next summary. Do not block.
6. Flag a downgraded premium gate role (atlas-security, atlas-reviewer, atlas-architect) so the user can re-run at full tier later.
7. Only stop and address the user if every tier including `inherit` is exhausted.

## Approval gates and Definition of Done

### Gate 1: Requirements
- [ ] Testable acceptance criteria
- [ ] Scope and out-of-scope stated
- [ ] Open questions closed or escalated to user via atlas-pm / atlas-ba

### Gate 2: Design
- [ ] NFRs stated with targets
- [ ] Key decisions recorded (ADRs or equivalent)
- [ ] Trade-offs documented

### Gate 3: Final delivery
- [ ] Tests pass (or gaps explicitly accepted)
- [ ] atlas-security and atlas-reviewer clear (or risks accepted)
- [ ] Docs updated where applicable

Do not mark a gate done until its checklist is satisfied and the user approves.

## Security and review gates

Insert atlas-security and atlas-reviewer before deployment. They verify charter conformance (simplicity, best practices, human voice), not only correctness. atlas-compliance joins when regulated data or compliance scope applies.

## Conflict resolution

When roles disagree (e.g. architect vs security): arbitrate by charter (simplicity, evidence, security first). If still unresolved, escalate to the user with options and a recommendation. No silent overrides.

## Run workspace

Create `.atlas/runs/<run-id>/` at kickoff. Standard artifacts:

- `requirements.md`, `design.md`, `test-plan.md`, `review.md`, `decisions.md`, `budget.md`
- Role-specific files as needed (e.g. `security.md`)

Use a short run id (date + slug, e.g. `2026-06-11-auth-refactor`).

## Enterprise specialists

Engage on demand when domain requires: network, sysinfra, cloud, dba, data-eng, data-sci, ai-eng, data-analyst, ent-arch, delivery, consultant, compliance.

## Onboarding (`/atlas-lead help`)

List all 24 roles, six workflow presets, three approval gates, token-budget summary, and point to `ROLES.md` for examples.

## References
- https://scrumguides.org/
