# Contributing to Atlas

Atlas is meant to be copied, extended, and shared. Keep it self-contained and lean.

## Ground rules

- Self-contained: no references to external skills, rules, or plugins. Vendor any methodology you need into the relevant playbook.
- Human-authored voice: no em dashes, proper punctuation, no AI tells or filler. This applies to every file, including this one.
- Token-lean: keep the always-on footprint to `rules/atlas-core.md`. Detail belongs in on-demand playbooks and the knowledge base.
- Cite sources for any standard or claim added to a playbook.

## Public repo hygiene

This repo is public. Before you open a pull request:

- **No secrets.** Do not commit API keys, tokens, `.env` files, or credentials of any kind.
- **No PII in `knowledge/`.** The knowledge base ships with the bundle. Keep `lessons.md`, `proposed.md`, `ways-of-working.md`, and `usage-insights.md` free of personal data, internal URLs, or customer-specific details. Use generic examples.

If you find sensitive data in a fork or local install, remove it before pushing. Report accidental exposure through GitHub Security Advisories if needed.

## Adding or editing a role

A role has three parts that must stay in sync:

1. `agents/atlas-<role>.md`: the agent. Frontmatter needs `name` (matching the filename, atlas-prefixed), `description` (what and when), `tier` (premium/standard/fast), `capabilities`, `permissions`, `skills`, `rules`, and `modelHints` (per-IDE model suggestions). Reviewer or audit roles set `permissions.readonly: true`.
2. `skills/atlas-<role>-playbook/SKILL.md`: the methodology, templates, and cited standards.
3. `manifest.json`: add the agent file and the skill directory so tracking works.

Each agent should include a `## Direct invocation` section (consultative) and a `## Pipeline invocation` section (autonomous, returns a handoff artifact).

## Editing lite mode

The lite agents, playbooks, and `lite/rules/atlas-core.md` are **generated**, not hand-authored (the other 4 `lite/rules/*.md` files and `lite/workflows/*.md` are small, self-contained, and don't need generation — they never had external references to drift). This exists so Atlas scales down to 3B-8B models with 4K-8K context, not just up to enterprise use — see the "Built to scale" value in `knowledge/reference/core-values-charter.md`.

If a role has a lite mode (currently: lead, dev, qa, architect, security — plus `rules/atlas-core.md`), its full source file (`agents/atlas-<role>.md`, `skills/atlas-<role>-playbook/SKILL.md`, or `rules/atlas-core.md`) ends with a `## Lite mode` section wrapping the exact lite content in markers:

```markdown
<!-- lite:start -->
...content for the generated lite/ file, including its own frontmatter if any...
<!-- lite:end -->
```

To change lite behavior: edit the block in the full source file, then run `python3 scripts/build-lite.py`. Never hand-edit a file under `lite/agents/`, `lite/skills/`, or `lite/rules/atlas-core.md` — it will be overwritten, and `python3 scripts/build-lite.py --check` (run this before opening a PR) will flag it as drift.

Adding lite support to a new role: append a `## Lite mode` block to its agent file and playbook, add both source-to-output pairs to the `SOURCES` list in `scripts/build-lite.py`, then generate. Keep the lite content genuinely small and self-contained — no references to `knowledge/` or the `k/` shorthand; a small model can't reliably skip content it's told to ignore, so lite files must not depend on that.

## File formats

- **Agents** (`agents/`): YAML frontmatter + markdown body.
- **Rules** (`rules/`): YAML frontmatter (`load: always|on-demand|contextual`) + markdown body.
- **Skills** (`skills/`): YAML frontmatter (`type: playbook|guide|reference`, `appliesTo`) + markdown body.
- **Knowledge** (`knowledge/`): YAML frontmatter (`category: framework|charter|process|template|reference`) + markdown body.
- **Workflows** (`workflows/`): YAML frontmatter (`type: pipeline|fast-lane|assessment`) + markdown body.

## Before you open a change

- Review all changed files for Cursor-specific references (model slugs, `Task` tool, `~/.cursor/`, `.mdc` extensions).
- Update `CHANGELOG.md` and bump `VERSION` when behavior changes.
- Do not commit secrets. Keep the knowledge base free of credentials and PII.
- Run `python3 scripts/validate-refs.py` and, if you touched a file with a `## Lite mode` block, `python3 scripts/build-lite.py --check`. Both should exit clean.
