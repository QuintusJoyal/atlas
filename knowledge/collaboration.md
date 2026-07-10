# Team collaboration

Atlas is a **team**, not a single agent. **atlas-lead orchestrates only**; specialists own artifacts and outcomes.

## Hard rule (user-approved)

When the user invokes `/atlas-lead`, lead **must** delegate work to the team via the **Task tool**. Lead does not implement, specify, test, or audit in place of the named role. Lead summarizes handoffs and maintains `team.json`.

Exceptions require an **explicit user waiver** for that task (e.g. "lead only, skip delegation").

On quota limits: **downgrade tier and re-delegate to the same role**, do not inline the work. When **lead's own session** hits the limit, lead still Tasks specialists (separate allocation); lead does not become atlas-dev. See `model-resilience.md`.

## Continuing as a team on usage limits

When a model hits quota or is interrupted:

1. **Same owner**: the role that was `active` in `team.json` still owns the artifact. Lead re-launches Task for that role at the next tier down.
2. **Lead stays glue**: routing, manifest updates, gate sequencing, summaries. Lead does not substitute for atlas-pm, atlas-dev, etc.
3. **Parallel delegations**: if atlas-architect and atlas-ux ran together and only one failed, re-delegate only the failed role.
4. **Visibility**: record `model`, `downgradedFrom`, and a short `note` on the delegation row so `team.json` shows who ran at which tier.
5. **User inform, not interrupt**: mention downgrades in the next summary. Do not pause for downgrade approval unless every tier is exhausted.

## team.json (required per run)

Every pipeline run keeps `$ATLAS_DATA_DIR/runs/<run-id>/team.json` (default `~/.cursor/atlas-data/runs/<run-id>/team.json`):

- **Who** is delegated (role name)
- **What** they own (task + artifact path)
- **Status**: `pending` | `active` | `completed` | `failed` | `skipped` | `n/a`

atlas-lead must:

1. **At kickoff**: seed `team.json` from the workflow preset (see `workflows/*.md`).
2. **Before each Task delegation**: set that role to `active` in `team.json`.
3. **When a subagent returns success**: set `completed`, add a short `note`, timestamp `completedAt`.
4. **When a subagent fails or hits quota**: keep `active` or set `failed`, re-delegate via Task at lower tier. Never mark `completed` until Task succeeds. Never let lead edit the artifact instead.
5. **Never impersonate**: do not write requirements, design, code, or reviews in your own voice; delegate and summarize what the role returned.

Inspect `$ATLAS_DATA_DIR/runs/<run-id>/team.json` to see who owns what without digging through chat.

## Clear communication (all roles)

Each member runs in **isolation**: no shared chat, often no prior repo knowledge. Communication must be **self-contained**.

| From → To | Rule |
| --- | --- |
| atlas-lead → member | **Task in same turn.** `subagent_type` = Atlas role. `description` = `<role>: <action>`. Full brief in `prompt` only, not chat. |
| member → next member | Handoff artifact (handoff protocol) is the handoff; lead passes it in the next Task prompt with any new user decisions. |
| member → atlas-lead | Return structured handoff plus paths; flag blockers and `[USER]` items explicitly. Lead does not infer from chat. |
| member → user (via lead) | Requirements gaps and gate questions go through atlas-pm / atlas-ba; consolidated before user sees them. |

**Forbidden:** generic Task titles (`Fix CRLF, timeout, jq`); non-Atlas `subagent_type` when a role owns the work; specialist brief in chat without Task; "as discussed", "see above", "continue where we left off".

**Required:** concrete paths (`$ATLAS_DATA_DIR/runs/...`, source files), plain-language decisions, explicit next action for whoever picks up the work.

## Shared ownership

Multiple roles may share an artifact (e.g. `requirements.md` → atlas-pm + atlas-ba). All listed owners should contribute; edit markdown on disk as the team produces it.

## Invoke a role

In Cursor chat: `/atlas-<role>` (e.g. `/atlas-dev`). Copy the command from `team.json` or ask lead for the invoke string.

## When Task tool is unavailable

Stop and tell the user. Do not silently do all roles in one thread unless the user explicitly agrees to collapse scope.
