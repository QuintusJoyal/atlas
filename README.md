# Atlas

**A shareable team of AI IDE agents for software delivery.**

Atlas is a self-contained bundle that gives you 24 specialist roles (PM, architect, dev, QA, security, and more) plus an orchestrator (`atlas-lead`) that can run a feature from requirements through review and deploy-ready handoff. Works on Cursor, Claude Code, OpenCode, VS Code Copilot, Windsurf, Antigravity, and any AI IDE that reads agents, rules, and skills from a project.

Run artifacts (requirements, gates, team state) live under `$ATLAS_DATA_DIR`, not in your project repos. Your codebase stays clean.

**License:** [MIT](LICENSE)

## Quick start

1. Copy or clone this bundle into your project.
2. Read `SETUP.md` — it has per-IDE install instructions, model tier mapping, and verification checklists.
3. Start working with your IDE's native agent system.

See `SETUP.md` for IDE-specific details (Claude Code AGENTS.md, VS Code Copilot instructions, OpenCode AGENTS.md, etc.).

## Not included

- **No credentials** ship with this bundle. Do not commit secrets or PII into `knowledge/` or run artifacts.

## What you get

- 24 specialist roles plus an orchestrator (`atlas-lead`). See [ROLES.md](ROLES.md).
- Per-role playbooks grounded in cited industry standards (OWASP, ISTQB, DORA, C4, WCAG, TOGAF, and more).
- Lazy-loaded context: one tiny always-on rule, everything else loads only when its topic is in motion.
- Mandatory kickoff: workflow, `budget.md`, per-role estimates before build ([budget-template.md](knowledge/reference/budget-template.md)).
- Graduated enforcement levels: `warn`, `standard`, or `strict` (chat prompts and gate sidecars under `$ATLAS_DATA_DIR/runs/<run-id>/gates/`).
- Gate DoD checks, pipeline blockers, waivers (non-waivable: security, compliance, reviewer).
- Learning loop: inbox promote/reject for `proposed.md`, usage-insights on run complete.
- Human-authored voice: output does not read as AI-generated (no em dashes, no AI tells).

**Atlas Framework v1** combines core values, enterprise operating discipline, and a hybrid runtime: the IDE's native agent system executes work; gate sidecars and disk artifacts under `$ATLAS_DATA_DIR/runs/` hold pipeline state.

## Workflow presets

See [workflows/README.md](workflows/README.md). Feature and infra use full kickoff; bugfix/hotfix use lite kickoff profiles. Hotfix still requires lightweight 2nd/3rd line security and reviewer pass at the final gate.

## Sample run

```
You: atlas-lead add CSV export to the reports page
atlas-lead: Workflow = feature. Estimation huddle predicts medium usage, proceeding.
            Phase 1 requirements -> atlas-pm + atlas-ba.
atlas-pm:   Draft stories and acceptance criteria. 2 open questions for you.
[Gate 1: requirements] You approve after answering the questions.
atlas-architect: Design with an ADR for streaming vs buffering large exports.
[Gate 2: design] You approve.
atlas-dev:  Implements the endpoint. atlas-docs drafts user docs in parallel.
atlas-qa:   Adds tests. atlas-reviewer reviews. atlas-security clears the change.
[Gate 3: final delivery] You approve.
atlas-devops: Ships behind a flag. atlas-maintenance gets the handoff notes.
```

## Model tiering

Atlas uses abstract model tiers. Each IDE maps tiers to its available models. See `SETUP.md` for the full mapping table.

- **Premium** (deep reasoning): atlas-architect, atlas-security, atlas-reviewer, atlas-ent-arch, atlas-cloud, atlas-compliance.
- **Standard** (balanced): atlas-lead (orchestrator only; saves premium for gate roles), atlas-pm, atlas-ba, atlas-ux, atlas-qa, atlas-devops, atlas-maintenance, atlas-network, atlas-sysinfra, atlas-dba, atlas-data-eng, atlas-data-sci, atlas-ai-eng, atlas-delivery, atlas-consultant.
- **Fast** (high-volume): atlas-dev, atlas-docs, atlas-data-analyst.

When atlas-lead's session hits quota, lead must still delegate to specialist roles (subagents use separate allocation). Lead must not collapse into inline implementation. See [knowledge/reference/model-resilience.md](knowledge/reference/model-resilience.md).

## Token budget

Predicted vs Actual lives in `budget.md` per run. **Actual is self-reported** until IDE token telemetry is available. Heavy runs require user approval at the token-budget gate.

## MCP integrations (optional)

Roles use MCP servers when present (Jira and Confluence, GitLab, browser) but never depend on them. Read-mode usage is free. Any write-mode action (create or update an issue, open a merge request, publish a page) is drafted and waits for your approval.

## Knowledge base

Installed to `$ATLAS_DATA_DIR/knowledge/`. Key Framework v1 docs (also in repo `knowledge/`):

- [core-values-charter.md](knowledge/reference/core-values-charter.md)
- [enterprise-org-model.md](knowledge/reference/enterprise-org-model.md)
- [atlas-framework.md](knowledge/reference/atlas-framework.md) (operator guide and dogfood checklist)

See [knowledge/reference/README.md](knowledge/reference/README.md) for shipped vs installed files. `lessons.md` is canonical. Roles append to `proposed.md` for your batch approval.
