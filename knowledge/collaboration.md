---
name: collaboration
category: process
load-when: Delegating work, managing team.json, understanding communication protocols
skip-when: Individual specialist work, no delegation needed
description: Atlas team collaboration model — delegation rules, team.json management, and communication protocols.
audience: [atlas-lead, all]
tags: [delegation, team-json, communication, orchestration]
---

# Team collaboration

Atlas is a **team**, not a single agent. **atlas-lead orchestrates only**; specialists own artifacts and outcomes.

## Quick Reference
- Lead delegates, specialists execute — lead never implements
- team.json tracks: who, what, status (pending/active/completed/failed)
- Every agent runs in isolation — handoffs must be self-contained
- Communication: lead→member via delegation, member→lead via handoff
- On quota failure: downgrade tier and re-delegate, never inline
- Concrete paths, plain language, explicit next actions

## Hard rule (user-approved)

When the user invokes atlas-lead, lead **must** delegate work to the team via delegation. Lead does not implement, specify, test, or audit in place of the named role. Lead summarizes handoffs and maintains `team.json`.

Exceptions require an **explicit user waiver** for that task (e.g. "lead only, skip delegation").

On quota limits: **downgrade tier and re-delegate to the same role**, do not inline the work. See `model-resilience.md`.

## team.json (required per run)

Every pipeline run keeps `$ATLAS_DATA_DIR/runs/<run-id>/team.json`:

- **Who** is delegated (role name)
- **What** they own (task + artifact path)
- **Status**: `pending` | `active` | `completed` | `failed` | `skipped` | `n/a`

atlas-lead must:

1. **At kickoff**: seed `team.json` from the workflow preset (see `workflows/*.md`).
2. **Before each delegation**: set that role to `active` in `team.json`.
3. **When a subagent returns success**: set `completed`, add a short `note`, timestamp `completedAt`.
4. **When a subagent fails or hits quota**: keep `active` or set `failed`, re-delegate at lower tier. Never mark `completed` until delegation succeeds. Never let lead edit the artifact instead.
5. **Never impersonate**: do not write requirements, design, code, or reviews in your own voice; delegate and summarize what the role returned.

Inspect `$ATLAS_DATA_DIR/runs/<run-id>/team.json` to see who owns what without digging through chat.

## Clear communication (all roles)

Each member runs in **isolation**: no shared chat, often no prior repo knowledge. Communication must be **self-contained**.

| From → To | Rule |
| --- | --- |
| atlas-lead → member | Delegation names the role. Title = `<role>: <action>`. Full brief in the delegation payload. |
| member → next member | Handoff artifact (handoff protocol) is the handoff; lead passes it in the next delegation. |
| member → atlas-lead | Return structured handoff plus paths; flag blockers and `[USER]` items. |
| member → user (via lead) | Requirements gaps go through atlas-pm / atlas-ba; consolidated before user sees them. |

**Required:** concrete paths, plain-language decisions, explicit next action for whoever picks up the work.

### "Works with" protocol

When a collaboration table lists `Works with` as a direction, it means bidirectional information exchange. Initiate when you have a question or need input — do not wait passively. Example: if atlas-dev `Works with` atlas-dba, and the dev needs schema clarification, delegate a question to atlas-dba directly (via atlas-lead) rather than guessing.

## Artifact ownership matrix

| Artifact | Owner | Reviewer | Gate |
|----------|-------|----------|------|
| requirements.md | atlas-pm | atlas-ba | Gate 1 |
| design.md | atlas-architect | atlas-reviewer | Gate 2 |
| code/* | atlas-dev | atlas-reviewer | Gate 3 |
| test-plan.md | atlas-qa | atlas-reviewer | Gate 3 |
| security.md | atlas-security | atlas-compliance | Gate 3 |
| pipeline.yml | atlas-devops | atlas-security | Gate 3 |
| README.md | atlas-docs | atlas-reviewer | Gate 3 |
| team.json | atlas-lead | - | - |
| budget.md | atlas-lead | - | - |
| decisions.md | atlas-lead | - | - |

Multiple roles may share an artifact (e.g. `requirements.md` → atlas-pm + atlas-ba). All listed owners should contribute; edit markdown on disk as the team produces it.

## Invoke a role

Use the appropriate IDE invocation for your environment (e.g. `atlas-dev`). Copy the command from `team.json` or ask lead for the invoke string.

## When delegation is unavailable

Stop and tell the user. Do not silently do all roles in one thread unless the user explicitly agrees to collapse scope.
