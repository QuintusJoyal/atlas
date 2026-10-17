---
name: intent-and-specifications
category: process
load-when: Starting a run as atlas-lead, or resolving conflicts and checking policies at gates
skip-when: Simple single-role edits with no governance implications
description: Intent and Specification engineering layer. Machine-readable goals, values, risk tolerances, and enforceable policies loaded at bootstrap.
audience: [lead, all]
tags: [governance, intent, specifications, bootstrap, gates]
---

# Intent and specifications

Atlas has two governance substrates above its workflows. They were previously
scattered across the `*-governance.md` rules and agent frontmatter. The layer
makes organizational goals and policies machine-readable so every agent in a
delegation chain works from the same context.

| Layer | Location | Answers |
| --- | --- | --- |
| Intent | `intent/*.yaml` | What should we optimize for? How do conflicting goals resolve? |
| Specifications | `specifications/*.yaml` | What rules must we obey? How strict, and where? |

This is the upstream layer that defines *what* agents optimize for and *how*
conflicts resolve. It does not replace the guardrail rules or workflow gates; it
feeds them.

## Intent schema (`atlas-intent/1.0`)

Required keys: `schema`, `id`, `name`, `goals`, `values`, `risk_tolerance`, `tradeoffs`.

```yaml
schema: atlas-intent/1.0
id: governance
name: <human label>
description: <one line>
goals:
  - id: right-outcome
    description: <what good looks like>
    weight: critical | high | medium | low
values:
  - id: transparency
    description: <behavioral expectation>
risk_tolerance:
  security: low | medium | high
  compliance: low | medium | high
tradeoffs:
  priority: [security, compliance, correctness, maintainability, performance, cost, speed]
```

- `goals` are outcomes agents should pursue. `weight` ranks importance; default `medium`.
- `values` are non-negotiables that shape behavior, not scoreable outcomes.
- `risk_tolerance` is per domain; `low` means avoid risk, `high` means accept risk for speed.
- `tradeoffs.priority` is an ordered list, highest priority first. It is the
  tie-breaker when two outputs conflict.

## Specification schema (`atlas-specification/1.0`)

Required keys: `schema`, `id`, `name`, `scope`, `policies`.

```yaml
schema: atlas-specification/1.0
id: delivery
name: <human label>
scope: global | role | phase
policies:
  - id: spec-security-pass
    description: <enforceable rule>
    severity: block | warn | info
    scope: global | role | phase
    applies_to: [security-sensitive]   # optional conditions, roles, or phases
    reference: knowledge/reference/quality-gates.md   # optional knowledge ref
```

- `severity`: `block` stops the gate, `warn` passes with a logged warning, `info` is advisory.
- `scope`: `global` applies everywhere, `role` to the named roles, `phase` to the named phases.
- `applies_to` narrows when a policy fires. Unknown conditions never match.
- `reference` points at the supporting knowledge file.

## Bootstrap integration

At run start, before kickoff, atlas-lead:

1. Loads every file under `intent/` and `specifications/`.
2. Builds a short `## Governance` summary: goals, values, risk tolerance,
   trade-off order, and the `block`/`warn` policies that apply to the run.
3. Injects that summary into the context block of **every** delegation brief so
   all agents share the same governance context.
4. Records the loaded intent/spec ids and hashes in `team.json` for audit.

## Conflict resolution

When two agent outputs conflict, atlas-lead arbitrates using intent, not preference:

1. Which output violates a `block` policy? If one does, it loses.
2. Otherwise, which output aligns with the higher-ranked `tradeoffs.priority` dimension?
3. If still tied, the one with the smaller scope change wins.
4. Record the arbitration, the winning and losing options, and the deciding
   dimension in `decisions.md`.

Arbitration is **advisory**: Atlas agents are prompt-driven, so the ordering
guides the recommendation the lead presents. It is not runtime enforcement.

## Policy compliance at gates

At each approval gate, atlas-lead validates the phase output against every
applicable policy:

- `block` violation: gate stays `failed`. Re-delegate to fix it, or ask the user
  for an explicit waiver (waivers are logged with actor and reason).
- `warn` violation: gate may pass; log the violation with severity and policy id.
- `info` violation: note it only.

Every violation is logged in `decisions.md` as
`policy <id> (<severity>): <what was found> - <artifact>`.

## Run-scoped overrides

Intent priority can be overridden for a single run. Atlas is IDE-hosted with no
runtime CLI, so overrides are declared in the run folder instead of shell flags:

```yaml
# $ATLAS_DATA_DIR/runs/<run-id>/intent-overrides.yaml
# equivalent to: --intent-overrides "performance>security"
overrides:
  - tradeoff: "performance>security"
    actor: <user>
    reason: <why>
    date: <ISO date>
```

Rules:

- Overrides affect the trade-off order only, for this run only.
- `block` policies cannot be overridden; only the user can grant a logged waiver.
- Every override is written to `decisions.md` with actor, reason, and date.
- At run complete, list active overrides in the summary so the audit trail is complete.

## Tooling

`python3 scripts/validate-refs.py` validates this layer:

- Every `intent/<file>.yaml` and `specifications/<file>.yaml` reference in `.md`
  files resolves to a real file.
- Each YAML file matches its schema (required keys, enums, unique ids).
- Policy `reference` paths resolve to real knowledge files.
