# Atlas

One team. Every discipline. Under your command.

Atlas is a self-contained, shareable team of Cursor subagents that covers the full software delivery lifecycle plus enterprise and consultancy roles. It drops into `~/.cursor/` on any machine and depends on nothing else in your setup.

## What you get
- 24 specialist roles plus an orchestrator (`atlas-lead`). See [ROLES.md](ROLES.md).
- Per-role playbooks grounded in cited industry standards (OWASP, ISTQB, DORA, C4, WCAG, TOGAF, and more).
- Lazy-loaded context: one tiny always-on rule, everything else loads only when its topic is in motion.
- A token-budget protocol that predicts heavy tasks and asks for your approval before spending.
- A shared knowledge base that the team reads from and proposes lessons into, for your batch approval.
- Workflow presets that right-size the pipeline per task.
- Human-authored voice: output does not read as AI-generated (no em dashes, no AI tells).

## Install
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

After installing, open Cursor and run `/atlas-lead help`.

## Use it
- Direct: `/atlas-pm draft stories for X`, `/atlas-security audit the auth module`, `/atlas-qa write tests for Y`. A directly invoked role is consultative: it asks clarifying questions and presents drafts so you can tune the work.
- Pipeline: `/atlas-lead take feature X from requirements to deploy-ready`. The orchestrator picks a workflow, delegates to roles, runs the approval gates, and keeps you in control.

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
- Premium (`claude-opus-4-8-thinking-high`): atlas-architect, atlas-security, atlas-reviewer, atlas-lead, atlas-ent-arch, atlas-cloud, atlas-compliance.
- Standard (`composer-2.5`): atlas-pm, atlas-ba, atlas-ux, atlas-qa, atlas-devops, atlas-maintenance, atlas-network, atlas-sysinfra, atlas-dba, atlas-data-eng, atlas-data-sci, atlas-ai-eng, atlas-delivery, atlas-consultant.
- Fast (`composer-2.5-fast`): atlas-dev, atlas-docs, atlas-data-analyst.

## MCP integrations (optional)
Roles use MCP servers when present (Jira and Confluence, GitLab, browser) but never depend on them. Read-mode usage is free. Any write-mode action (create or update an issue, open a merge request, publish a page) is drafted and waits for your approval.

## Knowledge base
Installed to `~/.cursor/atlas-knowledge/`. `lessons.md` is the canonical set every role reads. Roles append candidate lessons to `proposed.md` for your batch approval. `usage-insights.md` is where atlas-ai-eng logs efficiency findings. Never store secrets or PII here.

## Validate
Run `./validate.ps1` or `./validate.sh` to lint frontmatter, check model IDs and playbook references, and flag em dashes and AI tells.

## Optional SDK orchestrator
`sdk/` holds an optional script that runs the same pipeline headlessly with the Cursor SDK, for CI or automation. It is not required to use Atlas. See [sdk/README.md](sdk/README.md).

## License
MIT. See [LICENSE](LICENSE).
