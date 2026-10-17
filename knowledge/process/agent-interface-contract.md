---
name: agent-interface-contract
category: process
load-when: Authoring or upgrading a skill, tool, or agent-facing API; reviewing interface descriptions; auditing bundle interfaces
skip-when: Editing implementation internals with no agent-facing surface
description: Agent-first interface contract for Atlas tools and skills. Defines schema completeness, description quality, naming, and versioning rules for every interface an agent consumes, enforced by scripts/lint-interfaces.py.
audience: [all]
tags: [interfaces, tools, skills, contracts, agent-first, schemas, descriptions]
---

# Agent interface contract

Services and bundles are becoming APIs meant to be called by agents, not people. An agent decides whether to use a tool or skill from its description and parameter schema alone — a vague description causes mis-routing, wasted context, and error loops. This document is the contract for every agent-facing interface in Atlas: skill manifests (`skills/*/SKILL.md`), tool definitions, and any surface an agent binds at runtime. The skill manifest schema itself lives in `knowledge/process/skill-registry.md`; this contract adds the quality layer on top of it.

## Quick Reference

| Concern | Rule | Enforced by |
|---------|------|-------------|
| Schema | Every interface declares the full required field set; no unknown fields | `scripts/lint-interfaces.py` |
| Description | One imperative sentence, 20–300 chars, ends with a period, names what the caller gets | `scripts/lint-interfaces.py` |
| Naming | kebab-case identifiers; name matches directory | `scripts/lint-interfaces.py` |
| Body sections | `Route`, `Scope` (with a `NOT` boundary); playbooks add `Delegation Examples` | `scripts/lint-interfaces.py` |
| Inputs/outputs | Every declared input and output is documented in the body | `scripts/lint-interfaces.py` |
| References | Every `k/<doc>` pointer resolves to a file under `knowledge/` | `scripts/lint-interfaces.py` |
| Versioning | Semver; breaking interface changes bump MAJOR | `scripts/validate-skills.py` |
| Validation | `python3 scripts/lint-interfaces.py` (also runs as step 5 of `scripts/validate-refs.py`) | — |

## Design principle: agent-consumable APIs

Design every interface to be called by an agent, not a person:

- **Descriptions route.** The description is the routing key. State what the caller gets ("returns structured pass/fail results"), not what the implementer does ("handles testing"). Lead with a verb.
- **Schemas are complete.** Declare every input and output in frontmatter and document each in the body with type/units/default and failure behavior. An agent must be able to bind the interface without reading the implementation.
- **Defaults are safe.** Omitted inputs must mean the poka-yoke (see `rules/atlas-core.md`) choice — read-only, scoped, reversible — never the destructive one.
- **Errors are structured.** Return what failed, why, and the shortest recoverable next step. Agents retry on environment errors, never on assertion failures; the interface must make that distinction machine-readable.
- **Narrow permissions.** Declare the smallest `permissions` set; broad access fails human review per `rules/security.md`.
- **No hidden context.** Anything project-specific is an input, not an assumption baked into the body — this is what keeps skills portable across projects.

## Schema rules

Base fields every `skills/<name>/SKILL.md` must carry (see `knowledge/process/skill-registry.md` for the full schema):

```yaml
---
name: my-skill                 # kebab-case; equals the directory name
description: One imperative sentence.  # 20-300 chars, ends with a period
type: skill                    # playbook | skill
appliesTo: [atlas-dev]         # bound agents, or [all]
tags: [testing, ci]
---
```

- No unknown frontmatter fields. Typos (`desciption`, `capabilites`) silently drop an interface out of agent discovery; the linter rejects them.
- `capabilities`, `permissions`, `inputs`, `outputs`, `requires` are lists when present; `version` is semver once `capabilities` is declared.
- Body sections: `## Route` (need → role/skill lines), `## Scope` (in-scope work `| NOT` out-of-scope work with an explicit boundary), and `## Delegation Examples` for playbooks. A skill that declares `inputs` or `outputs` documents each one in the body.

## Description quality

The description is the only text an agent sees when choosing among 25+ skills. It must:

1. Be a single sentence, 20–300 characters, ending with a period.
2. Start with a verb or state the artifact the caller receives ("Run a project's test suite and report structured pass/fail results…"), never a vague claim ("Various testing help").
3. Name the bound agent for playbooks (e.g. `Engineering playbook for atlas-dev.`), so routing and description agree.
4. Avoid banned filler: `various`, `etc.`, `and more`, `stuff`, `things`, `as needed`.

## Naming conventions

- Identifiers (skill names, capabilities, permissions, inputs, outputs, tags) are kebab-case: `^[a-z0-9]+(-[a-z0-9]+)*$`.
- `name` equals the directory name; the two drifting breaks discovery and integrity pinning.
- Knowledge pointers use `k/<stem>` and must resolve to `knowledge/**/<stem>.md`. Stems are globally unique; do not create a second file with an existing stem.

## Versioning

Follows the skill-registry contract: semver in frontmatter, same MAJOR = compatible, removing an input/output or renaming a capability is a MAJOR bump, and a MAJOR bump updates every dependent listed in `requires` in the same change.

## Validation

```
python3 scripts/lint-interfaces.py        # this contract
python3 scripts/validate-skills.py        # registry schema, deps, cycles
python3 scripts/validate-refs.py          # runs both plus integrity
```

An audit pass over the 24 playbook skills and `test-runner` is clean as of this document; run the linter after any interface change to keep it that way.

## Lite mode

Lite mode (3B–8B models) ships this contract doc only — no lite copies of skills' full interfaces and no in-context contract text. Lite roles inline their own essentials (`manifest.json` → `lite.knowledgeNote`); interface validation is a full-bundle, author-time concern, not something a small model does at runtime.
