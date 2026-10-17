---
name: effect-ledger
category: process
load-when: Retry or resume after failure, before any write-mode tool call (MCP write, git push, API POST), aborting a run, reconciling state after restore
skip-when: Read-only work, runs with no external side effects
description: Idempotent tool execution and compensating transactions for agent side effects. Append-only effects.jsonl ledger, deterministic idempotency keys, LIFO compensation registry.
audience: [atlas-lead, all]
tags: [idempotency, compensation, saga, side-effects, rollback, ledger, jsonl]
---

# Effect ledger

Atlas persists checkpoints and retries failed calls, but a retried "create ticket" must not silently become two tickets. This protocol gives every external side effect a deterministic identity, an append-only record, and an undo plan. It is the agent-side counterpart to the sagas described in `knowledge/infra/event-driven-architecture.md`, which cover software Atlas builds, never Atlas's own tool actions.

Because Atlas runs prompt-only through the host IDE, nothing mechanically intercepts a tool call. Dedup and rollback are enforced by convention: every role checks the ledger before a write and records every write after it. The IDE can implement the checks via hooks, but the convention is the contract.

## Quick Reference
- Ledger: append-only JSONL at `$ATLAS_DATA_DIR/runs/<run-id>/effects.jsonl`
- One entry per write-mode action: tool, args hash, idempotency key, result, compensation
- Idempotency key derived from the intended action; identical intent = identical key
- Before any write-mode retry: grep the ledger for the key; if an entry shows `applied`, reuse its result — never re-execute
- On unrecoverable failure or abort: run compensating operations LIFO (most recent applied effect first)
- Lite mode: the ledger covers filesystem edits only (Edit/Write); no MCP, git push, or API entries

## Schema

Each entry is a single JSON line:

```jsonl
{
  "ts": "2026-10-12T18:00:00Z",
  "role": "atlas-dev",
  "tool": "mcp.createIssue",
  "action": "create",
  "argsHash": "sha256:9f2c…",
  "idempotencyKey": "ik-7d4a1b",
  "status": "applied",
  "result": {"issueId": 4821, "url": "https://…"},
  "compensation": {"type": "mcp.deleteIssue", "args": {"issueId": 4821}, "status": "pending"},
  "checkpointId": "cp-20261012-003",
  "notes": "Create Jira ticket for story AT-17"
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `ts` | yes | ISO 8601 timestamp |
| `role` | yes | Agent role that performed (or attempted) the action |
| `tool` | yes | Tool name: `write`, `edit`, `bash`, `git.push`, `mcp.<verb>`, `api.post`, or `api.delete` |
| `action` | yes | Effect verb: create, update, delete, push, exec |
| `argsHash` | yes | `sha256:` + hash of the canonicalized arguments (sorted keys, volatile fields like timestamps excluded) |
| `idempotencyKey` | yes | Deterministic key for the intended action — see derivation below |
| `status` | yes | `planned`, `applied`, `failed`, `deduped`, `compensated`, `non-compensable` |
| `result` | conditional | Tool output needed for dedup replay (resource id, revision, exit code). Required when `status=applied` |
| `compensation` | conditional | The undo operation: `{type, args, status}`. Status: `pending`, `applied`, `failed`, `none`. `none` only when the tool has no safe inverse |
| `checkpointId` | no | Checkpoint the effect belongs to (links to ACP) |
| `error` | no | Error message when `status=failed` |
| `notes` | no | Human-readable intent, so a resume can judge whether the effect is still wanted |

## Idempotency keys

The key is derived from the **intended action**, not the call attempt. Same intent, same key, across retries, resumes, and role re-delegations.

Derivation:

1. Pick the fields that define the effect's identity: tool name + semantic target + semantic payload. Exclude volatile fields: timestamps, session ids, retry counters, approval text, output truncation markers.
2. Canonicalize: sorted keys, stable string form.
3. `idempotencyKey = "ik-" + first 12 hex chars of sha256(canonical form)`.

Examples:

| Action | Key inputs | Not in key |
|--------|-----------|------------|
| Create issue | tool, project, title, body hash | timestamp, reporter |
| Update record | tool, record id, changed-field names, new-value hash | revision number returned by the last attempt |
| Git push | tool, remote, ref, commit sha being pushed | local wall-clock |
| API POST | tool, endpoint, idempotency-relevant payload hash | request id, auth header |
| File edit (lite) | tool, absolute path, hash of replacement text | line numbers drift after prior edits |

An idempotency key may be supplied by the target system when it supports native idempotency (e.g. an `Idempotency-Key` header). When present, use the system-issued key and record the derived key in `notes`.

## Dedup protocol

Before executing a write-mode tool call:

1. Derive the idempotency key.
2. Grep `effects.jsonl` for that key.
3. Branch:
   - Entry `applied`: **do not re-execute.** Append a new entry with `status: "deduped"` and reuse the recorded `result`. Report the original resource to the caller.
   - Entry `compensated`: the effect was undone. A new execution is a genuinely new action: derive the key again including a disambiguator (e.g. attempt ordinal in `notes`) and proceed.
   - Entry `failed` or `non-compensable`: escalate to the user before retrying. The previous attempt's state is unknown or irreversible.
   - No entry: append `planned`, execute, then append `applied` (with `result`) or `failed`.

Never execute a write-mode call whose key already shows `applied` without going through this protocol — including after context compaction, checkpoint restore, or role handoff. Trajectory entries (`knowledge/process/trajectory-logging.md`) record decisions; the ledger records external effects. Both are needed.

## Compensation registry

Every write-mode tool class has a designated inverse. The compensation is captured **before** execution (the "before" state), because after execution it may no longer be available.

| Tool class | Compensation | Notes |
|-----------|--------------|-------|
| `edit` / `write` (filesystem) | Restore prior file content (or delete the file if it did not exist) from the pre-edit read or tool receipt | Always compensable; the pre-edit Read is the backup |
| `bash` (command with side effects) | Inverse command defined at plan time (e.g. `rm` of a created temp path, `kill` of a spawned background process) | If no safe inverse exists, mark `non-compensable` before running |
| `git.push` | **None.** Reverting requires force-push or a follow-up revert commit | Mark `non-compensable`; a revert commit is a new action with its own ledger entry |
| `mcp.create*` | `mcp.delete*` on the returned resource id | Capture the id from `result` |
| `mcp.update*` | `mcp.update*` restoring the pre-change field values | Snapshot prior values before executing |
| `mcp.delete*` | **None** (or recreate from a captured snapshot if the tool supports it) | Mark `non-compensable`; ask the user before deleting |
| `api.post` | Compensating `api.delete` or reversal endpoint, when the API offers one | Register the inverse endpoint at plan time |
| `api.delete` | Usually none | Mark `non-compensable`; ask the user |

Roles keep this registry current: when a new MCP server or API is onboarded during a run, define its compensation mapping before the first write and record it in `notes` on the first ledger entry.

## LIFO rollback

When a run aborts, hits an unrecoverable failure, or the user cancels after side effects exist:

1. Identify all entries with `status: "applied"` and `compensation.status: "pending"`.
2. Execute compensations in **reverse order of application** (last applied effect first, matching saga backward recovery).
3. After each compensation, append an entry with `status: "compensated"` and `compensation.status: "applied"`, or `compensation.status: "failed"` with the error.
4. If a compensation fails: stop the rollback and escalate to the user with the remaining uncompensated list. Never continue silently and never claim the run is clean.
5. Entries marked `non-compensable` are reported to the user as lingering effects, in application order, with their `notes` describing intent.

Rollback never deletes ledger entries. The ledger's value is the complete history of what happened, including what could not be undone.

## Checkpoint and recovery integration

- Checkpoint before the first risky write of a phase (per `knowledge/process/checkpoint-protocol.md`); ledger state is part of what a checkpoint restores.
- On restore or resume, run the reconciliation pass: for every `applied` entry since the checkpoint, verify the effect still exists and is still wanted. If yes, leave it; if it is stale, compensate it as a new decision; never re-apply an identical effect "just in case" — that is what the dedup protocol prevents.
- Retry loops from model resilience (`knowledge/reference/model-resilience.md`) and the tool-failure path in `knowledge/process/runtime-execution.md` consult the ledger before any write-mode retry. Retrying a read is free; retrying a write requires a dedup check.
- Handoffs include the applied-effect count and the last ledger key so the receiving role can continue the ledger without re-deriving state.

## Lite mode

Lite agents do not load external knowledge files and run without MCP or API tools, so the lite ledger covers filesystem edits only:

- One `effects.jsonl` per run, same path and schema, same append-only rule.
- Record `edit`/`write` effects with `idempotencyKey` (path + replacement-text hash) and `compensation` (restore prior content, or `none` for newly created files where deletion is the inverse).
- Before re-running an edit after a failure or context loss, check the ledger for the key. If it shows `applied`, verify the file already contains the change and skip the duplicate edit.

## Example flow

```text
atlas-dev: creating ticket AT-17. Key ik-7d4a1b not in effects.jsonl.
  append planned {tool: mcp.createIssue, argsHash: sha256:9f2c…, compensation: mcp.deleteIssue}
  execute → issueId 4821
  append applied {result: {issueId: 4821}, compensation.status: pending}

[session dies; resume from checkpoint]

atlas-dev: retrying ticket AT-17. Key ik-7d4a1b found, status=applied.
  append deduped. Reusing issueId 4821. No second ticket.

[later phase fails unrecoverably]

atlas-lead: aborting run. LIFO rollback:
  compensate ik-7d4a1b → mcp.deleteIssue 4821 → append compensated.
  Ledger: 4 entries. External state: clean.
```

## Anti-patterns

- Executing a write-mode call without deriving and checking its idempotency key first
- Recreating a resource after resume because "the tool call failed" without checking whether it actually landed (the failure may have occurred after the remote effect)
- Marking a compensation `none` for convenience when a safe inverse exists
- Rolling back forward as well as backward (compensating an effect the user wants kept)
- Editing or deleting ledger entries to tidy up after a failure
- Treating compensation as risk-free: deleting a wrongly created issue can itself fail or delete the wrong thing — verify the target id from `result` before compensating
