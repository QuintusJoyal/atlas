---
name: delegation-authority
category: process
load-when: Spawning subagents, auditing a delegation, investigating an incident involving agent authority
skip-when: Single-role tasks, direct user requests with no delegation
description: Authority semantics for artifact-based delegation — least-privilege attenuation, delegation tokens, and the append-only chain record used for post-hoc reconstruction.
audience: [atlas-lead, all]
tags: [delegation, authority, attenuation, least-privilege, audit, chain, security]
---

# Delegation authority propagation

When a role is spawned with a brief, its effective tool scope must be **strictly attenuated** from the delegator's. Authority flows down a delegation chain; it never widens on the way down, and every deviation routes back up to atlas-lead or a human gate.

This is convention-plus-validator, not a runtime sandbox: Atlas has no hook that can physically block a subagent from calling a tool. Enforcement is a compliance obligation on every role, a CI/script check on briefs and chain records, and an audit trail for post-hoc reconstruction. Treat a violated chain as a security finding, not a formatting error.

## Quick Reference
- Delegated scope ⊂ delegator scope — **strict subset, never equal, never greater**
- Subagents may never re-broaden their own scope; escalation goes to atlas-lead (T2) or the user (T3)
- Every spawn carries a delegation token: original principal, chain, and attenuated scope
- Chain edges are appended to `$ATLAS_DATA_DIR/runs/<run-id>/delegation-chain.jsonl` (append-only)
- Lite mode: attenuation only, no chain storage
- Validate with `python3 scripts/validate-delegation.py`

## Attenuation rule

For every spawn edge (delegator D → delegatee E):

```
scope(E) ⊂ scope(D)     # strict subset: |scope(E)| < |scope(E) ∪ scope(D)| and scope(E) ⊆ scope(D)
```

Concretely:
1. Every tool in E's scope must be in D's scope (no invention from below).
2. E's scope must drop at least one tool D holds, unless the lead documents an explicit, user-approved exception for a leaf task (the default is zero exceptions).
3. Read-only qualifiers attenuate: `Bash:read-only` is a valid attenuation of full `Bash`, not a new capability.
4. Role-specific permanent overrides (see `knowledge/process/role-tool-scoping.md`) apply **before** attenuation, never after.

**No re-broadening.** A subagent that needs a tool outside its scope does not widen itself, does not ask a peer to spawn it with more scope, and does not re-interpret its brief. It escalates: document what is needed and why, escalate to atlas-lead (T2); the lead either re-delegates the sub-task to a role that already has the tool, or routes the expansion to the user (T3/HITL). An escalation that would make the requester's scope equal to or greater than its own delegator's is denied by default.

## Delegation token

Every brief carries a delegation token. It is the authority record for that spawn; a brief without one is incomplete and must be rejected by the receiving role.

```json
{
  "token": {
    "id": "d-002",
    "principal": "user",
    "chain": ["user > atlas-lead:d-001", "atlas-lead > atlas-dev:d-002"],
    "delegate": "atlas-dev",
    "scope": ["Read", "Grep", "Glob", "Write", "Edit", "Bash:read-only"],
    "delegatorScope": ["Task", "Read", "Grep", "Glob", "Write", "Edit", "Bash"],
    "authorizedBy": "atlas-lead",
    "runId": "2026-10-17-feature-42"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Unique edge id (`d-N`), stable for the run |
| `principal` | yes | Original human/user principal the whole chain answers to |
| `chain` | yes | Ordered path of `delegator > delegate:edge-id` hops from the principal to this edge |
| `delegate` | yes | Role being spawned |
| `scope` | yes | Attenuated tool scope granted to the delegate |
| `delegatorScope` | yes | The delegator's own effective scope at spawn time (the superset for the attenuation check) |
| `authorizedBy` | yes | Who approved this edge: `user`, `atlas-lead`, or a named gate role |
| `runId` | yes | Run the edge belongs to |

## Chain record (append-only)

Each spawn appends one JSON line to the run's chain record. **Never rewrite or delete existing lines** — corrections are new lines (e.g. an `escalate` or `revoke` action) so the audit history stays monotonic.

The root edge's `scope` is the run's **authority envelope** — the full tool set the principal permits the chain to pass down. It is usually broader than the lead's own operational scope (atlas-lead itself never Edits, Writes, or Runs Bash; orchestration scope is self-imposed, the envelope is what it may grant). Attenuation is checked against the envelope, edge by edge, down the chain.

Store at: `$ATLAS_DATA_DIR/runs/<run-id>/delegation-chain.jsonl`

```jsonl
{"ts":"2026-10-17T14:30:00Z","id":"d-001","action":"spawn","principal":"user","delegator":"user","delegate":"atlas-lead","parent":null,"scope":["Task","Read","Grep","Glob","Write","Edit","Bash"],"authorizedBy":"user"}
{"ts":"2026-10-17T14:31:00Z","id":"d-002","action":"spawn","principal":"user","delegator":"atlas-lead","delegate":"atlas-dev","parent":"d-001","scope":["Read","Grep","Glob","Write","Edit","Bash:read-only"],"authorizedBy":"atlas-lead"}
{"ts":"2026-10-17T14:40:00Z","id":"d-003","action":"escalate","principal":"user","delegator":"atlas-dev","delegate":"atlas-lead","parent":"d-002","scope":[],"authorizedBy":"atlas-lead","why":"Needs Bash:full for migration rehearsal"}
```

Actions: `spawn` (new edge), `escalate` (scope-deviation request routed upward), `grant` (lead/user approved an expansion — a **new** edge, not an edit), `revoke` (edge voided; its descendants are suspended until re-authorized).

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `ts` | yes | ISO 8601 timestamp |
| `id` | yes | Edge id, unique in the file |
| `action` | yes | spawn / escalate / grant / revoke |
| `principal` | yes | Original principal for the whole chain |
| `delegator` | yes | Role granting the authority (or requesting escalation) |
| `delegate` | yes | Role receiving it (`escalate` targets are upward) |
| `parent` | yes | Parent edge id, `null` only for the principal's first edge |
| `scope` | yes | Attenuated scope on this edge (empty for pure escalations) |
| `authorizedBy` | yes | Approver identity |
| `why` | no | Escalation/revoke justification |

## Chain reconstruction (incident response)

Given a chain record, reconstruct "who authorized what, upon whose authority":

1. **Root.** Find the edge(s) with `parent: null` — authority originates with the user (or the human gate named in `authorizedBy`).
2. **Path.** For any delegate, walk `parent` links to the root. The walk is the authorization path: every hop's `scope` must be a strict subset of its parent hop's scope.
3. **Breadth.** Group edges by `delegator` to see what each role handed down; diff a delegate's `scope` against the sum of its children to spot over-granting.
4. **Deviation.** Every `escalate` without a later `grant` edge is an unauthorized-deviation attempt; every `grant` names who approved it.
5. **Blast radius.** `revoke` an edge and all descendants with `parent` links into it lose authority retroactively — list them by walking the parent links.

Validate and reconstruct mechanically:

```
python3 scripts/validate-delegation.py --chain $ATLAS_DATA_DIR/runs/<run-id>/delegation-chain.jsonl
python3 scripts/validate-delegation.py --delegator "Read,Grep,Glob,Write" --delegatee "Read,Grep,Glob"
```

The script fails on any edge that is not strictly attenuated from its parent, on broken parent links, and on duplicate edge ids — the same conditions an incident review looks for first.

## Lite mode subset

Lite mode enforces **attenuation only**: the lead must still narrow scope below its own on every spawn, and a subagent still escalates rather than re-broadening. Lite skips the chain record (no `delegation-chain.jsonl`, no token plumbing in the 4-section handoff) — 8K-context models spend the budget on the task, not the audit trail. The lite rule lives in `lite/rules/handoff-protocol.md`.

## Related

- `knowledge/process/role-tool-scoping.md` — phase tool matrix and the brief format the token plugs into
- `knowledge/process/tool-registry.md` — tool names and delegation pattern
- `knowledge/context/escalation-tiers.md` — T1/T2/T3 routing for deviation requests
- `rules/handoff-protocol.md` — handoff artifact that carries the token between phases
