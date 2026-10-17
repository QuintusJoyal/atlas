---
name: mcp-server-governance
category: process
load-when: Onboarding, updating, or revoking an MCP server; auditing MCP usage; deciding whether a server may be mounted
skip-when: Normal read-mode MCP use on already-approved servers
description: Lifecycle governance for MCP servers — trust catalog, onboarding review, version pinning, revocation kill-switch, and audit wiring.
audience: [atlas-lead, atlas-security, all]
tags: [mcp, governance, trust-catalog, supply-chain, security, audit]
---

# MCP server lifecycle governance

Atlas may mount third-party MCP servers (Jira, Confluence, GitLab, browser, and any others). This is a supply-chain boundary: a mounted server can read anything the agent can read and, in write mode, act in external systems. This document defines which servers may be mounted at all, and how they are onboarded, pinned, revoked, and audited.

**Scope.** This governs server admission (may this server be mounted?). It is distinct from the runtime tool-permission engine (may this role call this tool right now? See `knowledge/process/role-tool-scoping.md`) and from A2A agent-to-agent concerns. The write-mode approval gate in `rules/atlas-core.md` still applies on top of everything here: read-mode is free, write-mode actions are drafted and need user approval.

**Opt-in.** With no catalog configured, behavior is unchanged. Governance activates only when a trust catalog exists at `$ATLAS_DATA_DIR/knowledge/reference/mcp-trust-catalog.yaml` (shipped as `knowledge/reference/mcp-trust-catalog.yaml`).

## Trust catalog

The catalog is a YAML registry (`schema: atlas-mcp-trust/1`) of permitted servers. Each entry declares:

| Field | Meaning |
|-------|---------|
| `id` | Unique kebab-case identifier |
| `name`, `owner` | Human name and the role accountable for the server |
| `version` | Exact `x.y.z` pin — never a range, never `latest` |
| `status` | `approved` (mountable), `review` (onboarding, not mountable), `revoked` (kill-switched) |
| `source` | Where the server comes from (package name, repo) |
| `capabilities` | Declared `tools`, `resources`, `prompts` — compared against the live server manifest at onboarding |
| `access` | Per-role scope: `read` (may use read-mode) and `write` (may draft write actions). `all` is valid in `read` only |
| `review` | `reviewed_by` + `reviewed_at` from the last onboarding or re-review |
| `revoked_at`, `revoked_reason` | Required when `status: revoked` |

Only `status: approved` servers may be mounted. Validate the catalog with `python3 scripts/validate-mcp-catalog.py` (skips cleanly when no catalog exists).

## Onboarding review

New servers start at `status: review` and are not mountable until the review completes:

1. **Source vetting.** Confirm the `source` is the vendor's official distribution. Record who requested the server and for what workflow.
2. **Declared vs actual capabilities.** Fetch the server's manifest (tools/resources/prompts it actually exposes, via `initialize` / `tools/list` in the MCP client, or the vendor's published manifest). Compare line by line against the entry's declared `capabilities`. Undeclared capabilities must be either declared and justified, or treated as a finding that blocks onboarding. Extra write-capable tools are the highest-risk deltas.
3. **Scope.** Grant `access.write` to the fewest roles that need it. Default new servers to read-only.
4. **Sign-off.** atlas-security records `review.reviewed_by` and `review.reviewed_at`, then flips `status` to `approved`. Re-run `python3 scripts/validate-mcp-catalog.py`.

If the IDE's MCP client cannot introspect a server's manifest, fall back to the vendor's published tool list and note the manual basis in the review.

## Version pinning and updates

- Entries pin an exact version. Range specifiers and `latest` are rejected by the validator: unpinned servers can silently ship new capabilities.
- Upgrades are re-reviews, not routine bumps: set `status: review`, compare the new manifest against the declared capabilities (the diff is where supply-chain changes hide), then re-approve with a fresh `reviewed_at`.
- If a vendor deprecates the pinned version, treat the upgrade exactly like onboarding.

## Revocation (kill-switch)

On compromise, a policy change, or a bad re-review:

1. Set `status: revoked` and clear `access.write` (and usually `access.read`). The validator rejects revoked entries that still carry write scope.
2. Record `revoked_at` and `revoked_reason`. Keep the entry — it is part of the audit trail.
3. **Disconnect the server immediately** in the IDE's MCP client. The catalog governs agent behavior; the IDE's native MCP client mounts servers independently, so revocation is only effective once the transport is disconnected too.
4. Do not re-mount under a new id without a fresh onboarding review.

## Audit

Every lifecycle-relevant MCP action is appended to the action trail (`$ATLAS_DATA_DIR/runs/<run-id>/trajectory.jsonl`, schema in `knowledge/process/trajectory-logging.md`):

| action | When |
|--------|------|
| `mcp_mount` | A server is mounted or unmounted; `target` is the server id, `outcome` reflects catalog status |
| `mcp_tool_call` | Any MCP tool is called; `target` is `server_id/tool_name`, `toolInput` summarized (no secrets) |
| `mcp_write` | A write-mode MCP action is drafted or executed; must carry the approval trail |

Use `mcp_revoke` (as `action`, `target` = server id) to record revocations within a run. Routine read-mode calls on approved servers may be sampled rather than logged exhaustively; mounts, write actions, and revocations are never sampled.

## Checklist

- [ ] Catalog exists and `validate-mcp-catalog.py` passes (or no catalog: skip everything)
- [ ] Server source is the vendor's official distribution
- [ ] Declared capabilities match the live server manifest
- [ ] Version pinned exactly; upgrades gated through re-review
- [ ] Access scope is least-privilege; write scope needs a named owner role
- [ ] Mounts, tool calls, and write actions land in `trajectory.jsonl`
- [ ] Compromise triggers revocation: catalog flipped, transport disconnected, reason recorded
