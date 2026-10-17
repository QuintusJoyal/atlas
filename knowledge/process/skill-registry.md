---
name: skill-registry
category: process
load-when: Authoring or upgrading a skill, resolving which skill can run a capability, debugging skill composition or version conflicts
skip-when: Using a single playbook with no composition needs
description: Skill marketplace conventions for Atlas. Defines the skill manifest schema, registry lookup by capability, semantic versioning rules, dependency resolution, and the per-session invocation audit log.
audience: [all]
tags: [skills, marketplace, registry, composition, versioning, capabilities]
---

# Skill registry

Atlas skills are versioned, capability-typed bundles that any agent can discover, claim, and compose. The registry is the `skills/` directory plus `manifest.json` — no runtime service. This document is the contract: the manifest schema every skill must follow, how agents resolve a need to a skill, and how composition stays conflict-free.

## Quick Reference

| Concern | Convention |
|---------|-----------|
| Manifest location | Frontmatter of `skills/<name>/SKILL.md` |
| Discovery | `manifest.json` → `skills[]`; capability lookup via frontmatter `capabilities` |
| Versioning | Semver (`MAJOR.MINOR.PATCH`) in frontmatter `version` |
| Backward compat | Same `MAJOR` = compatible; a major bump must update every dependent listed in `requires` |
| Dependencies | Frontmatter `requires[]`; each entry must name an existing skill and minimum version |
| Conflicts | Two skills may not share a `name`; a `requires` cycle or unresolvable version is a conflict |
| Audit | One line per invocation appended to `$ATLAS_DATA_DIR/skill-audit.log` (see below) |

## Skill manifest schema

Every `skills/<name>/SKILL.md` carries YAML frontmatter. Base fields (all skills):

```yaml
---
name: test-runner                 # must equal the directory name
description: One-line purpose.   # what the skill does, for catalog listing
type: skill                       # playbook | skill
appliesTo: [all]                  # agent names, or [all] for cross-agent skills
tags: [testing, ci, quality]
---
```

Extended fields (marketplace skills — required for any skill that declares capabilities, permissions, or dependencies):

```yaml
version: 1.0.0                    # semver; required once capabilities is present
capabilities: [test-execution]    # capability tags other skills/agents resolve against
permissions: [read-files, run-commands]  # what the skill may touch; human-approval applies
inputs: [scope]                   # logical input names; document each in the body
outputs: [result, exit-code]      # logical output names; document each in the body
requires: []                      # dependencies: "skill-name@MAJOR.MINOR.MINIMUM"
```

Rules enforced by `scripts/validate-skills.py`:

1. `name` matches the directory name; `description` is non-empty.
2. If `capabilities` is present, `version` is present and valid semver.
3. `permissions`, `inputs`, `outputs`, `requires` (when present) are non-empty lists or `[]`.
4. Every `requires` entry names a skill that exists in the registry, in the form `name@X.Y.Z`.
5. No two skills share a `name`; no `requires` cycles exist.

## Registry API (static)

There is no server. The registry surface is files plus one validator:

- **Register**: add `skills/<name>/SKILL.md` with the schema above, add `<name>` to `manifest.json` → `skills[]`, re-pin hashes (`python3 scripts/verify-integrity.py --update`).
- **Query**: list skills from `manifest.json`; filter by `capabilities` / `tags` by reading frontmatter. Agents should present the skills whose `appliesTo` includes them (or `all`).
- **Resolve**: given a need, pick the skill whose `capabilities` contain the tag. If several match, prefer the highest compatible `MINOR` within the same `MAJOR`; a skill that another bound skill already `requires` wins over an unbound duplicate.
- **Validate**: `python3 scripts/validate-skills.py` — runs as step 4 of `scripts/validate-refs.py`, so the existing Validate Bundle CI covers it.

## Versioning and backward compatibility

- Semver: `MAJOR` for breaking input/output or permission changes, `MINOR` for backward-compatible capability additions, `PATCH` for fixes.
- A consumer writing `requires: [test-runner@1.2.0]` accepts any `1.x.y >= 1.2.0` and rejects `2.x`. Dependency resolution therefore never silently crosses a major boundary.
- Removing a capability tag or renaming an output is a `MAJOR` bump. Bumping a `MAJOR` requires updating every skill that lists the skill in `requires` in the same change — the validator flags a dependent pinned to a mismatched major as a conflict.

## Dependency resolution and conflict detection

Before binding a skill chain, resolve in dependency order and fail on:

- **Missing dependency** — a `requires` entry naming no registered skill.
- **Version conflict** — two dependents requiring incompatible majors of the same skill (e.g. `test-runner@1.x` and `test-runner@2.x` in one chain).
- **Cycle** — `a requires b requires a`.
- **Permission escalation** — a composed chain whose union of `permissions` exceeds what the session's human approval covers; the chain must not run, per the human-approval posture in `rules/security.md`.

On conflict, do not improvise: report the conflicting pair and escalate to the orchestrator or human, matching `knowledge/context/escalation-tiers.md`.

## Invocation audit log

Every skill binding writes one append-only line to `$ATLAS_DATA_DIR/skill-audit.log` (fallback: the project's `.atlas/` data home):

```
<ISO-8601 UTC>|<agent-role>|<session-id>|<skill-name>@<version>|<status>|<summary>
```

- `status` ∈ `bound`, `invoked`, `failed`, `denied`.
- `session-id` is the orchestrator's handoff artifact id (see `knowledge/process/checkpoint-protocol.md`); reuse it across a chain so one session's skills are reconstructable.
- `summary` is one short phrase (e.g. `exit=0 214 passed`), never file contents or secrets.
- The log is evidence for retros and incident review; it is not loaded into context by default.

## Composition conventions

- **Claim, don't fork.** An agent claims a skill by binding it; never copy a skill body into an agent. Agents stay thin; skills carry the workflow.
- **Chain via outputs→inputs.** Compose by mapping one skill's `outputs` to the next skill's `inputs`. Document each mapping in the handoff artifact.
- **Narrow permissions.** Declare the smallest `permissions` set; a skill asking for broad write access will fail human review.
- **Cross-project portability.** A skill must not reference paths or secrets outside the host project; anything project-specific belongs in `inputs`. This is what makes `test-runner` usable across projects unchanged.

## Example: test-runner

`skills/test-runner/SKILL.md` is the reference marketplace skill: versioned (`1.0.0`), capability-typed (`test-execution`), permission-scoped (`read-files`, `run-commands`), and bound by `appliesTo: [all]` so any agent in any project can claim it. See that file for the schema in practice.
