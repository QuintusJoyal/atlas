# Atlas

**A shareable team of Cursor subagents for software delivery.**

Atlas is a self-contained bundle you install into `~/.cursor/`. It gives you 24 specialist roles (PM, architect, dev, QA, security, and more) plus an orchestrator (`atlas-lead`) that can run a feature from requirements through review and deploy-ready handoff. No plugins or external skills required.

Run artifacts (requirements, gates, team state) live under `$ATLAS_DATA_DIR` (default `~/.cursor/atlas-data/`), not in your project repos. Your codebase stays clean.

**License:** [MIT](LICENSE)

## Quick start

### Install

The bundle mirrors the `~/.cursor/` layout. Install copies `agents/`, `skills/`, and `rules/` into `~/.cursor/`, and `knowledge/` into `~/.cursor/atlas-knowledge/`.

Windows (PowerShell):

```
./install.ps1            # install
./install.ps1 -Mode update     # re-sync, preserves your knowledge base edits
./install.ps1 -Mode uninstall
```

macOS / Linux (bash):

```
./install.sh             # install
./install.sh update      # re-sync, preserves your knowledge base edits
./install.sh uninstall
```

After installing, **start a fresh `/atlas-lead` chat** so new rules and agents load. Preserved KB files (`lessons.md`, `proposed.md`, `ways-of-working.md`, `usage-insights.md`) are not overwritten on update. Optional: `./scripts/merge-knowledge.ps1` to copy new bundle knowledge files.

### Use

- **Direct:** `/atlas-pm draft stories for X`, `/atlas-security audit the auth module`, `/atlas-qa write tests for Y`. A directly invoked role is consultative: it asks clarifying questions and presents drafts so you can tune the work.
- **Pipeline:** `/atlas-lead take feature X from requirements to deploy-ready`. The orchestrator picks a workflow, runs mandatory kickoff, delegates via Task, runs approval gates, and keeps you in control.

## Not included

- **Control Center** (Signal Deck operator UI and SDK runner) is a separate repo: [`atlas-control-center`](https://github.com/QuintusJoyal/atlas-control-center) (clone as a sibling directory). Install scripts here do not deploy it. The Cursor SDK orchestrator lives in that repo under `sdk/`, not in this bundle.
- **No credentials** ship with this bundle. Do not commit secrets or PII into `knowledge/` or run artifacts.

## What you get

- 24 specialist roles plus an orchestrator (`atlas-lead`). See [ROLES.md](ROLES.md).
- Per-role playbooks grounded in cited industry standards (OWASP, ISTQB, DORA, C4, WCAG, TOGAF, and more).
- Lazy-loaded context: one tiny always-on rule, everything else loads only when its topic is in motion.
- Mandatory kickoff: workflow, `budget.md`, per-role estimates before build Tasks ([budget-template.md](knowledge/budget-template.md)).
- Graduated enforcement levels: `warn`, `standard`, or `strict` (chat prompts and gate sidecars under `$ATLAS_DATA_DIR/runs/<run-id>/gates/`).
- Gate DoD checks, pipeline blockers, waivers (non-waivable: security, compliance, reviewer).
- Learning loop: inbox promote/reject for `proposed.md`, usage-insights on run complete.
- Human-authored voice: output does not read as AI-generated (no em dashes, no AI tells).

**Atlas Framework v1** combines core values, enterprise operating discipline, and a hybrid runtime: Cursor Task executes work; gate sidecars and disk artifacts under `$ATLAS_DATA_DIR/runs/` hold pipeline state.

## Workflow presets

See [workflows/README.md](workflows/README.md). Feature and infra use full kickoff; bugfix/hotfix use lite kickoff profiles. Hotfix still requires lightweight 2nd/3rd line security and reviewer pass at the final gate.

## Sample run

```
You: /atlas-lead add CSV export to the reports page
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

Set per role in each subagent's frontmatter. Models are account-specific; adjust if your plan differs, or use `inherit`.

- Premium (`claude-opus-4-8-thinking-high`): atlas-architect, atlas-security, atlas-reviewer, atlas-ent-arch, atlas-cloud, atlas-compliance.
- Standard (`composer-2.5`): **atlas-lead** (orchestrator only; saves premium for gate roles via Task), atlas-pm, atlas-ba, atlas-ux, atlas-qa, atlas-devops, atlas-maintenance, atlas-network, atlas-sysinfra, atlas-dba, atlas-data-eng, atlas-data-sci, atlas-ai-eng, atlas-delivery, atlas-consultant.
- Fast (`composer-2`): atlas-dev, atlas-docs, atlas-data-analyst.

When **atlas-lead's session** hits quota, lead must still **Task** specialist roles (subagents use separate allocation). Lead must not collapse into inline implementation. See [knowledge/model-resilience.md](knowledge/model-resilience.md).

## Token budget

Predicted vs Actual lives in `budget.md` per run. **Actual is self-reported in v1** until Cursor token telemetry is available. Heavy runs require user approval at the token-budget gate.

## MCP integrations (optional)

Roles use MCP servers when present (Jira and Confluence, GitLab, browser) but never depend on them. Read-mode usage is free. Any write-mode action (create or update an issue, open a merge request, publish a page) is drafted and waits for your approval.

## Knowledge base

Installed to `~/.cursor/atlas-knowledge/`. Key Framework v1 docs (also in repo `knowledge/`):

- [core-values-charter.md](knowledge/core-values-charter.md)
- [enterprise-org-model.md](knowledge/enterprise-org-model.md)
- [atlas-framework.md](knowledge/atlas-framework.md) (operator guide and dogfood checklist)

See [knowledge/README.md](knowledge/README.md) for shipped vs installed files. `lessons.md` is canonical. Roles append to `proposed.md` for your batch approval.

## Validate

Run `./validate.ps1` or `./validate.sh` to lint frontmatter, check model IDs and playbook references, and flag em dashes and AI tells.

## Control Center (optional)

Signal Deck operator UI and the optional SDK runner live in the sibling repo [`atlas-control-center`](https://github.com/QuintusJoyal/atlas-control-center). Install scripts here do not deploy them. From that repo: `cp .env.example .env` then `docker compose up -d --build` (see its `README.md`, `REFERENCE.md`, and `sdk/README.md`). Archived product history: [docs/archive/CONTROL-CENTER-PLAN.md](docs/archive/CONTROL-CENTER-PLAN.md).
