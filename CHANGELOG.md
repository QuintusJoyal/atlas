# Changelog

All notable changes to Atlas are recorded here. This project follows semantic versioning.

## [Unreleased]

## [0.4.0] - 2026-06-17

### Added

- **Central data home:** run state, gates, tickets, config, jobs, and activity live under `$ATLAS_DATA_DIR` (default `~/.cursor/atlas-data/`), not in project repos. Migration scripts: `scripts/migrate-to-atlas-data.ps1` and `.sh`.
- **Control Center split:** Signal Deck UI moved to standalone sibling repo `atlas-control-center`. This bundle keeps agents, rules, skills, knowledge, and optional SDK only.

### Changed

- README and framework docs updated for public GitHub; Control Center plan archived under `docs/archive/`.
- Install scripts create `~/.cursor/atlas-data/` alongside the knowledge base.

## [0.3.0] - 2026-06-12

### Added (Atlas Framework v1)
- **Hybrid runtime:** kickoff validator, gate DoD evaluator, delegation checks via chat and repo artifacts.
- Graduated enforcement via chat prompts and gate sidecars (`warn` | `standard` | `strict`).
- Waiver flow with non-waivable 2nd/3rd line DoD; force-approve audit trail in gate sidecars.
- KB promote/reject inbox actions; auto usage-insights row on final gate.
- Six workflow plans with RACI fields on delegations.
- Knowledge: `core-values-charter.md`, `enterprise-org-model.md`, `atlas-framework.md`, `retro-template.md`.
- `scripts/merge-knowledge.ps1`.

### Changed
- Root README: Framework v1 positioning, install/post-update.
- `atlas-lead`: kickoff and gate checks via chat and repo artifacts.
- Legacy runs (no `frameworkVersion: 1`): warn-only enforcement.

## [0.2.5] - 2026-06-12

### Added
- Mandatory pipeline **kickoff**: workflow announcement, estimation huddle via Task, `budget.md` from `knowledge/budget-template.md`, per-role estimates before first specialist Task.
- `team.json` fields: `workflowRationale`, `kickoffAt`, `budget` (predicted + roleEstimates).

### Changed
- `workflows/feature.md`, `bugfix.md`, README: Phase 0 kickoff documented.
- `atlas-lead` agent and playbook: kickoff blocking sequence; "delegate early" means kickoff huddle, not skip estimates.
- `handoff-protocol`, `atlas-ai-eng-playbook`: required role estimates in handoffs and huddle output format.

## [0.2.4] - 2026-06-12

### Changed
- **atlas-lead default model** moved from premium to **standard** (`composer-2.5`) so orchestration does not burn opus quota; premium stays for gate roles via Task.
- Documented **lead self-limit** failure mode: when the orchestrator session hits quota, lead must still Task specialist roles; forbidden to collapse into inline implementation.
- Updated `atlas-lead-orchestration.mdc`, `agents/atlas-lead.md`, `model-resilience.md`, playbook, README tier list.

## [0.2.3] - 2026-06-12

### Added
- `rules/atlas-lead-orchestration.mdc` (always-on): hard stop when Task fails or hits quota. Lead's only recovery is re-delegate same role at lower tier; explicit forbidden actions and phrases.

### Changed
- `agents/atlas-lead.md`: quota interrupt moved to top with allowed/forbidden table; removed "quick glue fix" loophole; token-budget vs model-quota split (budget pause waits for user; model quota re-delegates immediately).
- `atlas-lead-playbook`, `model-resilience.md`, `atlas-core.mdc`: anti-patterns for lead absorbing work after interrupt; wrong/right examples.

## [0.2.2] - 2026-06-12

### Changed
- Team continuity on usage limits: atlas-lead must **re-delegate Task to the same role** at a downgraded tier instead of absorbing work inline. Documented in `model-resilience.md`, `collaboration.md`, `atlas-lead` agent, `atlas-lead-playbook`, `atlas-core.mdc`, and `team-charter.mdc`.
- `team.json` delegations may record `model` and `downgradedFrom` for manifest visibility when a role was re-delegated after quota interrupt.

## [0.2.1] - 2026-06-11

### Changed
- atlas-lead now delegates every phase to the named role via the Task tool by default and must not impersonate roles by writing their output in its own voice. If the Task tool is unavailable, it raises that with the user instead of absorbing all roles into one thread. Updated the `atlas-lead` agent, the `atlas-lead-playbook` skill, and added an Orchestration lesson.

## [0.2.0] - 2026-06-11

### Added
- Automatic model downgrade (model resilience): when a model is quota-limited, rate-limited, unavailable, or blocked, roles and atlas-lead retry the affected step one tier down (premium to standard to fast to inherit) and continue without interrupting the workflow.
- `knowledge/model-resilience.md`: the canonical tier cascade, triggers, behavior, logging format, and premium-gate quality flag.
- Downgrade logging in `usage-insights.md` and the run `budget.md`, surfaced to the user in the next summary.
- Tier-cascade retry logic in `sdk/orchestrator.ts`, with per-phase starting tiers and a premium-gate downgrade flag.

### Changed
- `atlas-core.mdc`, `team-charter.mdc`, `handoff-protocol.mdc`, `atlas-lead` (agent and playbook), and `atlas-ai-eng` updated for the no-interruption downgrade policy and downgrade tracking.

## [0.1.0] - 2026-06-11

### Added
- Initial Atlas bundle: a self-contained, shareable team of Cursor subagents.
- 12 core SDLC roles (atlas-pm, atlas-ba, atlas-architect, atlas-ux, atlas-dev, atlas-qa, atlas-security, atlas-reviewer, atlas-devops, atlas-maintenance, atlas-docs) plus the orchestrator atlas-lead.
- 12 enterprise specialists (atlas-network, atlas-sysinfra, atlas-cloud, atlas-dba, atlas-data-eng, atlas-data-sci, atlas-ai-eng, atlas-data-analyst, atlas-ent-arch, atlas-delivery, atlas-consultant, atlas-compliance).
- Per-role playbook skills grounded in cited industry standards.
- Lazy-loaded rules: always-on atlas-core plus agent-requestable team-charter, handoff-protocol, writing-style, and glob-scoped engineering-standards.
- Quota-aware model tiering (premium, standard, fast) and a token-budget protocol.
- Shared knowledge base with a proposal queue, ways-of-working, and usage-insights.
- Workflow presets: feature, bugfix, data-project, infra-change, security-audit, discovery.
- Installer (install, update, uninstall) with manifest-driven file tracking, plus self-validation scripts.
- Human-authored voice standard (no em dashes, no AI tells), enforced by atlas-reviewer and validation.
