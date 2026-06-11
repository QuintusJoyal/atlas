# Atlas Control Center (first mission brief)

Atlas's first dogfooding project after the bundle ships: a **platform-independent monitoring and workflow dashboard** that runs outside the IDE and lets the user monitor and approve Atlas work in one place.

## Problem

Today, pipeline progress lives in chat and scattered files under `.atlas/runs/`. Approval gates, token budgets, and MCP write drafts need a single surface the user can open without Cursor.

## Goals

1. **Pipeline board**: SDLC phases plus gates with live node status per run.
2. **Role cards**: all 24 roles with current task, model tier, and status.
3. **Live transcripts**: per-role stream via Cursor SDK `run.stream()`.
4. **Approval inbox**: token-budget pre-approvals, three gates, MCP-write drafts, proposed KB and ways-of-working items.
5. **Token meter**: predicted vs actual by tier, with overrun alerts.
6. **Knowledge browser**: read `~/.cursor/atlas-knowledge/` without opening the IDE.

## Non-goals (v1)

- Replacing Cursor as the execution environment.
- Figma or design-tool integration.
- Cloud Automations / cron triggers (optional later).

## Integration seam

Build on `sdk/orchestrator.ts` (or Python equivalent):

- `Agent.create` + `agent.send` per phase
- Thread context between roles via run workspace artifacts
- Stream events to the UI
- Explicit `wait()` and dispose per SDK best practices

## Suggested stack (kickoff decision)

Chosen at kickoff by atlas-pm and atlas-architect. Keep portable:

- Local web app (e.g. Vite + React) or local TUI
- Reads/writes `.atlas/runs/` and `~/.cursor/atlas-knowledge/`
- Optional Cursor Canvas as lightweight in-IDE complement

## Success criteria

- User can see active run status without opening agent chat.
- All three approval gates actionable from the inbox.
- Token budget visible before and during runs.
- Zero dependency on external skills; Atlas bundle only.

## Kickoff prompt (when ready)

```
/atlas-lead run discovery for Atlas Control Center v1 using knowledge/control-center-brief.md
```

Then: requirements gate, design, build, and dogfood on real Atlas runs.
