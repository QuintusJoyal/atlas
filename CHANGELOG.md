# Changelog

All notable changes to Atlas are recorded here. This project follows semantic versioning.

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
