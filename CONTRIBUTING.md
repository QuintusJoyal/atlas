# Contributing to Atlas

Atlas is meant to be copied, extended, and shared. Keep it self-contained and lean.

## Ground rules

- Self-contained: no references to external skills, rules, or plugins. Vendor any methodology you need into the relevant playbook.
- Human-authored voice: no em dashes, proper punctuation, no AI tells or filler. This applies to every file, including this one.
- Token-lean: keep the always-on footprint to `rules/atlas-core.mdc`. Detail belongs in on-demand playbooks and the knowledge base.
- Cite sources for any standard or claim added to a playbook.

## Public repo hygiene

This repo is public. Before you open a pull request:

- **No secrets.** Do not commit API keys, tokens, `.env` files, or credentials of any kind.
- **No PII in `knowledge/`.** The knowledge base ships with the bundle. Keep `lessons.md`, `proposed.md`, `ways-of-working.md`, and `usage-insights.md` free of personal data, internal URLs, or customer-specific details. Use generic examples.
- **Run validate.** Execute `./validate.ps1` (Windows) or `./validate.sh` (macOS/Linux) and fix any reported issues.

If you find sensitive data in a fork or local install, remove it before pushing. Report accidental exposure through GitHub Security Advisories if needed.

## Adding or editing a role

A role has three parts that must stay in sync:

1. `agents/atlas-<role>.md`: the subagent. Frontmatter needs `name` (matching the filename, atlas-prefixed), `description` (what and when), and `model` (from the allowed set). Reviewer or audit roles add `readonly: true`.
2. `skills/atlas-<role>-playbook/SKILL.md`: the methodology, templates, and cited standards.
3. `manifest.json`: add the agent file and the skill directory so install, update, and uninstall track them.

Each subagent should include a `## Direct invocation` section (consultative) and a `## Pipeline invocation` section (autonomous, returns a handoff artifact).

## Allowed models

`claude-opus-4-8-thinking-high` (premium), `composer-2.5` (standard), `composer-2` (fast), or `inherit`. If a model is unavailable on an account, use `inherit`.

## Before you open a change

- Run `./validate.ps1` (Windows) or `./validate.sh` (macOS/Linux). It checks frontmatter, model IDs, playbook references, and flags em dashes and AI tells.
- Update `CHANGELOG.md` and bump `VERSION` when behavior changes.
- Do not commit secrets. Keep the knowledge base free of credentials and PII.
