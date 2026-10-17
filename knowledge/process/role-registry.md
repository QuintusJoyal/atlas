---
name: role-registry
category: process
load-when: Delegating roles, defining a new role, checking capability boundaries, auditing role assignments, adapting a role to a risk level
skip-when: Single-role work, routine delegation to an unchanged role
description: Agent Specialization Registry (ASR). Centralized, validated role definition schema plus a role-based access control model, pre-delegation checks, an audit-trail convention, and a risk-adaptive policy matrix. Runtime isolation is host-dependent and marked as such, not claimed.
audience: [atlas-lead, atlas-ent-arch, atlas-security, all]
tags: [rbac, roles, governance, capabilities, permissions, audit, risk, registry]
---

# Agent Specialization Registry (ASR)

The Agent Specialization Registry is Atlas's governance layer for role specialization. Where the skill/playbook mechanism answers "what can this role do well" (discovery), the registry answers "what is this role allowed to touch, and how do we prove it" (governance and enforcement).

The registry is **derived, not duplicated**. Each role's definition is its agent frontmatter plus the `## Role Boundaries` (I DO / I DO NOT) section in `agents/atlas-<role>.md`. A centralized, machine-readable view is produced by `scripts/validate-roles.py --json`; that output is the registry. Nothing in this file restates per-role data, so the registry cannot drift from the role definitions.

## Honest scope

Atlas is a declarative markdown bundle. It can define, validate, and check roles; it can record audit events. It cannot isolate a host platform's tools on its own. The enforcement levels below are explicit about which is which, so a team does not read "RBAC" here as a security boundary the bundle cannot actually hold.

| Level | Mechanism | Enforced by | Status |
| --- | --- | --- | --- |
| **L0** Schema + static validation | Field contract, capability lists, boundary sections, manifest cross-check | `scripts/validate-roles.py`, run by `scripts/validate-refs.py` in CI | Enforced |
| **L1** Pre-delegation check | atlas-lead checks the target role's capabilities and permissions before delegating | atlas-lead, per `rules/atlas-lead-orchestration.md` | Enforced by convention (declarative) |
| **L2** Runtime enforcement | OS/IDE sandbox, tool allow-list, file and network scope | Host IDE / platform | **Host-dependent.** Atlas ships the contract, not the mechanism — see "Host adapter contract" |

## Role definition schema

Every specialist role is defined by these fields. `scripts/validate-roles.py` fails when a required field is missing, mis-typed, or inconsistent with the manifest.

| Field | Type | Meaning | Level |
| --- | --- | --- | --- |
| `name` | string | Role id, `atlas-<slug>`, must equal the filename stem | L0 |
| `role` | string | Human-readable role label | L0 |
| `description` | string | Routing hint used by atlas-lead | L0 |
| `tier` | enum: `premium` \| `standard` \| `fast` | Default model tier | L0 |
| `capabilities` | string[] | Declared capability domains — what the role may do. Non-empty. | L1 |
| `permissions.read` | bool | May read project resources | L1 |
| `permissions.write` | bool | May write project resources, scoped by the role boundary | L1 |
| `skills` | string[] | Playbook skill id(s) | L0 |
| `rules` | string[] | Governing rules loaded with the role | L0 |
| `boundaries` | I DO / I DO NOT lists (body) | Prohibited actions; the authority on what the role refuses | L1 |
| `memory` | enum: `project` (optional) | Whether the role keeps project-scoped memory | L0 |

Boundaries are the second half of the capability boundary: `capabilities` is the allow-list, `## Role Boundaries` is the deny-list. Where the two disagree, **I DO NOT wins** (`ROLES.md`). The always-on `role-adherence` critic checks every deliverable against the producing role's own lists — see `knowledge/critic-prompts/role-adherence.md`.

## RBAC model

Atlas uses a flat role-based access control model (RBAC0) with an advisory constraint layer (phase and risk). It does not implement role inheritance or delegated administration.

| Concept | Atlas mapping |
| --- | --- |
| Subject | An Atlas role (`atlas-*`) |
| Resource | Resource class (table below) |
| Action | `read`, `write`, `execute`, `delegate` |
| Permission | `(subject, resource, action)`, derived from `capabilities`, `permissions`, and boundaries |
| Constraint | Phase scope (`knowledge/process/role-tool-scoping.md`) and risk level |

### Resource classes

| Class | Examples | Write-capable roles (frontmatter `write: true`) |
| --- | --- | --- |
| `source` | application code, tests | atlas-dev, atlas-qa, atlas-data-eng, atlas-data-sci |
| `docs` | README, changelogs, runbooks | atlas-docs, atlas-ai-eng |
| `infra` | IaC, CI config, deploy manifests | atlas-devops, atlas-sysinfra, atlas-cloud, atlas-dba, atlas-maintenance |
| `data` | schemas, migrations, pipelines | atlas-dba, atlas-data-eng, atlas-data-sci, atlas-data-analyst |
| `project-state` | `team.json`, `budget.md`, `decisions.md`, run folder | atlas-lead only |

The coarse `permissions.read`/`permissions.write` booleans are the frontmatter contract. Phase-aware tool scoping in `knowledge/process/role-tool-scoping.md` is the finer-grained, phase-level view and takes precedence when the two differ. Secrets (`secrets`) and production execution (`production`) are never granted by default; a role that needs either must be granted it explicitly in a brief, and the grant is recorded in the audit trail.

Non-waivable gate roles: `atlas-security`, `atlas-compliance`, and `atlas-reviewer` cannot be waived regardless of variant (`rules/team-charter.md`).

## Pre-delegation check (L1)

Before atlas-lead delegates, it runs the registry check for the target role:

1. **Capability fit** — does the brief's work fall inside the role's `capabilities` and I DO list?
2. **Permission fit** — does the work need a resource the role can write (or read) per its `permissions` and the resource table?
3. **Boundary fit** — does the brief ask for anything on the role's I DO NOT list? If so, route to the owning role instead (`ROLES.md` ownership table).
4. **If a needed permission is missing** — do not silently widen the role. Either split the task to the owning role, or grant the specific resource/action in the brief and record a `permission-grant` audit entry.

A delegation that fails the check is a routing error, not a role failure. Treated as a failed route in `knowledge/process/decision-quality-scoring.md`'s Delegation Accuracy when that opt-in scoring is on.

## Audit trail

Role assignments and permission decisions are append-only, one JSONL line each, at:

```
$ATLAS_DATA_DIR/runs/<run-id>/permission-audit.jsonl
```

The schema reuses `knowledge/process/trajectory-logging.md` field conventions and adds role-governance fields:

```jsonl
{"ts":"2026-10-17T14:30:00Z","role":"atlas-lead","action":"role-assignment","target":"atlas-dev","capabilities":["implementation","tdd","clean-code"],"phase":"implementation","risk":"medium","decision":"granted","why":"brief matches capabilities"}
{"ts":"2026-10-17T14:31:00Z","role":"atlas-dev","action":"permission-check","resource":"source","op":"write","decision":"allowed","rule":"permissions.write"}
{"ts":"2026-10-17T14:32:00Z","role":"atlas-dev","action":"permission-check","resource":"secrets","op":"read","decision":"denied","rule":"capability-boundary","why":"secrets not granted for this role"}
{"ts":"2026-10-17T14:33:00Z","role":"atlas-lead","action":"permission-grant","target":"atlas-dev","resource":"infra","op":"write","decision":"granted","why":"deploy flag change, brief-scoped","expires":"phase:implementation"}
```

| Field | Required | Description |
| --- | --- | --- |
| `ts` | yes | ISO 8601 timestamp |
| `role` | yes | Role making the decision (usually atlas-lead) |
| `action` | yes | `role-assignment`, `permission-check`, `permission-grant`, `permission-deny` |
| `target` | on assignment | Role being assigned or granted |
| `resource` / `op` | on check/grant | Resource class and operation |
| `decision` | yes | `granted`, `allowed`, `denied` |
| `rule` | on denial/allow | Which rule decided (`permissions.write`, `capability-boundary`, ...) |
| `risk` | on assignment | Risk level from the matrix below |
| `expires` | on grant | Scope of a temporary grant; grants are not standing |
| `why` | yes | One-line reason |

Audit entries are capped at one line each and record decisions, not routine reads — same density rule as trajectory logging. When the host provides a real sandbox, its own logs are the L2 source of truth; this file is the Atlas-level decision record.

## Risk-adaptive role policy

Risk level is determined at kickoff from the task and the conditions in `agents/atlas-lead.md` (auth/payment/secret → security-sensitive; compliance → regulated; data model → data-changes). Atlas-lead applies the matching row when writing the delegation brief and records the level in the audit trail. Adaptation is a **policy decision applied at delegation time**, not an automatic runtime hook.

| Risk | Typical trigger | Capability scope | Tier floor | Extra gate |
| --- | --- | --- | --- | --- |
| `low` | docs, tests, isolated refactor | role default | any | none |
| `medium` | source code, API, non-prod config | role default, resource table applies | standard | reviewer |
| `high` | auth, secrets, payments, data model, prod-bound config | least-privilege subset; `secrets` read denied unless the role owns it | premium | security + reviewer |
| `critical` | prod deploy, irreversible migration, regulated data | read-only or dry-run; break-glass only | premium | security + compliance + explicit user sign-off |

Rules that never adapt away:
- Non-waivable gate roles (`atlas-security`, `atlas-compliance`, `atlas-reviewer`) keep their gate at every level.
- `secrets` and `production` are denied by default at all levels; a critical-level need is an explicit user sign-off, not an implicit escalation.
- Raising risk may add gates or lower tier, never remove a required gate.

## Integration with the orchestration runtime

The registry is consumed by the orchestration runtime (issue #6, `rules/atlas-lead-orchestration.md`) at the delegation step:

1. atlas-lead derives the registry via `scripts/validate-roles.py --json` at run start (or on demand).
2. The pre-delegation check above runs before every delegation.
3. Assignments and checks are appended to `permission-audit.jsonl`.
4. The `team.json` delegation row may carry `riskLevel` alongside the existing `downgradedFrom` field.
5. The `role-adherence` critic enforces the deny-list half of the boundary after the fact.

## Host adapter contract (L2, host-dependent)

For a host to enforce roles rather than merely advise, it must:

1. Read `agents/<role>.md` frontmatter (`permissions`, `capabilities`) and this file's resource table.
2. Map each permission to its sandbox primitive (tool allow-list, file scope, network scope, credentials).
3. Deny tool calls outside the role's permission and resource scope, and emit its own permission log the audit trail can correlate against.

Atlas does not ship or abstract these primitives; the contract above is what a host implements. Until a host does, treat L1 as the working boundary and L2 as aspirational, not as a claim.

## Validation

```bash
python3 scripts/validate-roles.py          # validate all role definitions
python3 scripts/validate-roles.py --json   # print the derived registry
```

`scripts/validate-refs.py` runs the validator as part of the existing Validate Bundle CI, so a malformed role definition, a missing boundary section, or an agent that is not listed in `manifest.json` fails the build rather than shipping.

## See Also
- `knowledge/process/role-tool-scoping.md` for phase-aware tool scope
- `knowledge/critic-prompts/role-adherence.md` for the boundary critic
- `knowledge/process/trajectory-logging.md` for the base audit schema
- `ROLES.md` for the ownership table and the secondary-role legend
- `rules/team-charter.md` for non-waivable gates
