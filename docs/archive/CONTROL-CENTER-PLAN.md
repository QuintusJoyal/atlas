> **Historical archive.** Not required for Atlas bundle users. For operators, see the sibling [atlas-control-center](https://github.com/QuintusJoyal/atlas-control-center) repo.

# Atlas Control Center - archived plan

## Revival status (2026-06-14)

Control Center was **restored and extended** in run `2026-06-14-control-center-sdk` (artifacts at `~/.cursor/atlas-data/runs/2026-06-14-control-center-sdk/`). Live code lives in the **standalone sibling repo** [atlas-control-center](https://github.com/QuintusJoyal/atlas-control-center); operator reference is in that repo's `REFERENCE.md`.

**Central data home (2026-06):** Run state, gates, tickets, and global config live under `$ATLAS_DATA_DIR` (default `$ATLAS_HOME/.cursor/atlas-data/` or `~/.cursor/atlas-data/`), not in project repos. Historical sections below still mention the old `.atlas/` layout. Treat those paths as **superseded**.

| Topic | Current path | Superseded (pre-2026-06) |
| --- | --- | --- |
| Quick start, stack summary | `atlas-control-center` repo `README.md` | - |
| API, types, deploy, runner | `atlas-control-center` repo `REFERENCE.md` | - |
| Host SDK runner and ingest | `sdk/README.md` (this repo) | - |
| Run artifacts (requirements, design, implementation) | `$ATLAS_DATA_DIR/runs/<run-id>/` (e.g. `~/.cursor/atlas-data/runs/2026-06-14-control-center-sdk/`) | `<repo>/.atlas/runs/<run-id>/` |
| Tickets, config, jobs, activity | `$ATLAS_DATA_DIR/work-items.json`, `config.json`, `runner-jobs.json`, `activity.jsonl` | `<repo>/.atlas/work-items.json`, `config.json` |
| Docker bind (host) | `.env`: `ATLAS_HOME`, `ATLAS_WORKSPACE_HOST`, `ATLAS_KB_HOST`; single `docker compose up` from sibling `atlas-control-center/` | `docker-compose.override.yml` with hard-coded paths |

Architecture: CC stays **keyless in Docker**; Cursor SDK runs on the **host** via `sdk/runner.ts`. Disk-backed features (runs, gates, inbox, KB, tickets) work without a runner; agent paths degrade explicitly when no runner heartbeat is present.

The sections below are **historical** (pre-purge archive, June 2026). They document product evolution and lessons learned; they are not the current operator guide.

---

This document was the only surviving artifact from the Control Center project after the June 2026 purge. All source code, Docker config, and run workspaces were removed at that time. The revival run above rebuilt from git history and this plan.

---

## 1. Original problem and goals

Atlas pipelines lived in Cursor chat and scattered files under `.atlas/runs/` *(superseded: now `$ATLAS_DATA_DIR/runs/`)*. The operator had no single place to see progress, approve gates, watch token spend, or browse the knowledge base without opening the IDE.

**Goals for v1:**

1. **Pipeline board** - SDLC phases and gates with live node status per run.
2. **Role cards** - all 24 Atlas roles with current task, model tier, and delegation status.
3. **Live transcripts** - per-role stream via Cursor SDK `run.stream()` and event ingest.
4. **Approval inbox** - token-budget pre-approvals, three gates (requirements, design, final), MCP-write drafts, proposed KB and ways-of-working items.
5. **Token meter** - predicted vs actual by tier, with overrun alerts (actual was self-reported until Cursor telemetry v2).
6. **Knowledge browser** - read and edit `~/.cursor/atlas-knowledge/` from the browser.

**Non-goals (v1):**

- Replacing Cursor as the execution environment.
- Figma or design-tool integration.
- Cloud automations or cron triggers.
- Canvas as a primary surface (deprioritized).

**Success criteria:**

- Operator sees active run status without opening agent chat.
- All three approval gates actionable from the inbox.
- Token budget visible before and during runs.
- Zero dependency on external skills; Atlas bundle only.

Kickoff prompt used: `/atlas-lead run discovery for Atlas Control Center v1 using knowledge/control-center-brief.md`

---

## 2. Product evolution

### Phase A - Framework v1 backend (June 2026)

Run `2026-06-11-control-center-v1` built the first working app:

- Express server on port **3847**, Vite + React client (dev on 5174 with API proxy).
- Reads/writes `.atlas/runs/` *(superseded)*, gate sidecars, `team.json`, `budget.md`, and `~/.cursor/atlas-knowledge/`. Revival uses `$ATLAS_DATA_DIR/runs/` instead.
- Pipeline state API, kickoff validator, gate DoD evaluator, delegation validator, graduated enforcement (`warn` | `standard` | `strict`).
- Six horizontal tabs: Pipeline, Workshop, Inbox, Team, Knowledge, Work.
- Docker Compose with mandatory `ATLAS_CC_TOKEN`, multi-workspace via `ATLAS_ROOTS`.
- SDK integration: set `ATLAS_CC_URL` and `ATLAS_CC_TOKEN`; orchestrator posts events to `/api/events/ingest`.

### Phase B - Signal Deck greenfield UI

Visual direction shifted from a settings-panel feel to an **operator console** named **Signal Deck**:

- Collapsible **58px icon rail** instead of horizontal tabs.
- **Top bar** with run chip, command palette (Cmd/Ctrl+K), live SSE indicator.
- **Deck home** dashboard as the default route.
- React Router for all destinations.
- Dark-first tokens (Syne display, Inter body, JetBrains Mono data).

Work tracking arrived as a portfolio overlay at `.atlas/work-items.json` *(superseded: `$ATLAS_DATA_DIR/work-items.json`)* with Kanban columns (backlog -> done). Later renamed to **Tickets** with ATL-native IDs (`ATL-...`), cycles, and agent chat per ticket.

Bidirectional features added: work-chat with agent runner, kickoff modal, activity SSE bus, operator avatar settings.

### Phase C - Frontend purge and Orbital rebuild

Incremental UI patches caused chrome drift (wrong theme scope, compose dock regressions, layout double-reserve bugs). The team **purged the entire client** to a placeholder shell while keeping the server intact (run `2026-06-13-frontend-purge-greenfield`).

Rebuild strategy (**Signal Deck Orbital**, run `2026-06-13-signal-deck-greenfield-v3`):

- **HTML-first**: literal CSS port from `signal-deck-orbital.html` into `orbital.css`.
- **13 reference frames** (00-12 canonical; additional PNG exports existed for QA).
- **1320x780 frame 01** (Mission Control / Deck) as the first sign-off gate.
- Metallic B&W chrome; color only on status badges.
- Theme on `.screen.dark` / `.screen.light`, not `html` or `:root`.
- Rail order: Deck -> Pipeline -> Stream -> Tickets -> Team -> Inbox -> Knowledge.
- Explicit chrome exclusions: no compose dock on primary routes, no Live badge in top bar, no right ActivityRail.

Final client routes before purge:

| Route | Purpose |
| --- | --- |
| `/` | Deck - situational overview, delegation graph placeholder, live ticker |
| `/pipeline`, `/pipeline/:runId` | Run list + inspector (Overview / Gates / Stream) |
| `/stream` | Cross-run activity telemetry |
| `/tickets`, `/tickets/board`, `/tickets/:id` | Ticket list, board, detail + agent chat |
| `/team`, `/team/:runId` | 24-role roster from `team.json` |
| `/inbox` | Gate, token budget, KB approvals; A/R shortcuts |
| `/knowledge`, `/knowledge/:file` | KB browse and edit |
| `/workshop`, `/workshop/:runId/:artifact` | Run markdown artifact editor |
| `/work` | Redirect to `/tickets` |

Overlays: command palette, kickoff modal, mobile bottom tab bar below ~768px.

---

## 3. Intended architecture

```
Operator browser
       |
       v
Control Center (Express + Vite SPA, localhost:3847)
       |
       +-- reads/writes --> Atlas workspace (.atlas/runs/, work-items.json, config.json)  [superseded -> $ATLAS_DATA_DIR/]
       +-- reads/writes --> ~/.cursor/atlas-knowledge/
       +-- SSE + REST <-- Cursor SDK agents (optional)
```

**Stack:**

| Layer | Technology |
| --- | --- |
| Client | Vite 6, React 19, React Router 7, `orbital.css` (no Tailwind in final Orbital build) |
| Server | Express 4, TypeScript via `tsx`, chokidar for file watch |
| Shared | `shared/types.ts`, `shared/chrome-routes.ts` |
| Tests | Node test runner on server (~93 tests at last count); Playwright e2e layout smoke @ 1320x780 |
| Container | Docker Compose, single port 3847, `Dockerfile` + optional `Dockerfile.e2e` |

**Key server APIs (representative):**

- Health and session: `GET /api/health`, `GET /api/session`
- Runs: `GET /api/runs`, `GET /api/runs/:id`, `GET /api/runs/:id/state`, kickoff preview/start
- Gates: `GET /api/runs/:id/gates/:gate/dod`, `POST /api/runs/:id/gates/:gate`, waivers, acknowledge
- Artifacts: list, read, write under run workspace
- Team: `GET/PUT /api/runs/:id/team`, delegate endpoint
- Inbox: `GET /api/inbox`; KB promote/reject
- Tickets/work: CRUD on `/api/tickets` (alias `/api/work`), chat + SSE streams, subtask generation
- Cycles: sprint-style grouping for tickets
- Activity: `GET /api/activity/stream`, `GET /api/agents/state`
- Events: `POST /api/events/ingest`, `GET /api/events/stream`
- Config: enforcement level, operator settings

**Security model:**

- POST/PUT/PATCH require `X-Atlas-CC-Token` from `GET /api/session`.
- CORS allowlist for localhost origins.
- Path traversal guards on run ids and filenames.
- Default bind `127.0.0.1`; Docker used `0.0.0.0` with mandatory token.

**Environment variables:**

| Variable | Purpose | Notes |
| --- | --- | --- |
| `ATLAS_DATA_DIR` | Central home for runs, tickets, config, jobs, activity | **Current** (default `~/.cursor/atlas-data/`) |
| `ATLAS_HOME` | User home for compose volume binds | **Current** (`.env`; replaces override file) |
| `ATLAS_WORKSPACE` / `ATLAS_WORKSPACE_HOST` | Code workspace (container + host) | **Current** |
| `ATLAS_ROOT` | Primary code workspace | Legacy alias; superseded by `ATLAS_WORKSPACE` |
| `ATLAS_ROOTS` | Comma-separated extra workspaces | **Deprecated** |
| `ATLAS_KB_DIR` | Knowledge base path (default `~/.cursor/atlas-knowledge`) | Still current |
| `ATLAS_CC_PORT` | Listen port (default 3847) | Still current |
| `ATLAS_CC_TOKEN` | Write auth token | Still current |
| `ATLAS_CC_URL` | SDK event ingest target | Still current |

**Integration with Atlas Framework v1:**

- `team.json` per run is authoritative for orchestration; Control Center displayed it on the Team tab.
- Gate sidecars at `.atlas/runs/<run-id>/gates/<gate>.json` *(superseded: `$ATLAS_DATA_DIR/runs/<run-id>/gates/`)* written on approve/reject.
- atlas-lead checked `GET /api/runs/:id/state` for blockers when Control Center was running.
- Legacy runs without `frameworkVersion: 1` got warn-only enforcement.

---

## 4. What was delivered before purge

- Full **Express backend** with pipeline validation, gate DoD, kickoff, work-chat agent runner, ticket/cycle store, activity bus, multi-workspace scan, Docker deployment.
- **Orbital React client** rebuilt from HTML reference: shell, all primary routes, typed API client, SSE hooks, command palette, kickoff modal, Playwright smoke tests passing.
- **Framework v1** docs and charter references wired to Control Center as the operator surface.
- **93 server unit tests**, production build ~260 kB main chunk, e2e layout smoke at desktop and mobile breakpoints.
- Reference assets: `signal-deck-orbital.html`, canonical frames 00-12 PNGs, architecture and requirements artifacts in `.atlas/runs/` *(superseded)* (those run folders were deleted with the purge; revival artifacts live under `$ATLAS_DATA_DIR/runs/`).

**Known gaps at time of archival:**

- Delegation graph on Deck used placeholder SVG, not live `team.json` layout.
- Token burn meter partly static until Cursor token telemetry v2.
- Drag-and-drop kanban not implemented (status change via API/actions only).
- Google Fonts loaded from CDN (offline mode was planned, not shipped).

---

## 5. Why stopped / status

**Status: archived, not maintained.**

Control Center was removed from the Atlas repo in run `2026-06-13-control-center-purge-final`. The product had consumed significant iteration on UI parity (multiple greenfield rebuilds) while the core Atlas bundle (24 roles, rules, knowledge, SDK) remained the primary deliverable. Maintaining a separate full-stack app alongside the agent bundle was judged out of scope for the repo going forward.

Gates, kickoff, token budget, and team visibility still work through **Cursor chat and disk artifacts** (`$ATLAS_DATA_DIR/runs/`, `team.json`, gate sidecars; formerly `.atlas/runs/` in project repos). No local dashboard enforces runtime blockers unless someone rebuilds from this plan.

---

## 6. Non-goals and notes for a revival

**If you pick this up again, treat these as constraints learned the hard way:**

1. **Do not incremental-patch UI** after a visual reset. Port reference CSS literally, then wrap in React.
2. **Theme scope** belongs on `.screen`, not `html` or `:root`.
3. **Rebuild the typed API client** before shipping routes; a read-only stub breaks all mutating flows.
4. **Frame 01 @ 1320x780** is the first human sign-off gate; do not wire all routes before chrome matches.
5. **Persistent docks** (compose, chat) need fixed/absolute positioning outside the main flex height chain.
6. **PNG reference sheets** can drift from canonical HTML; re-export from HTML before QA sign-off.
7. **E2E Docker**: Playwright version must match base image; share network with app container for CORS.

**Suggested revival sequence:**

1. Restore server from git history (tag or commit before purge).
2. Restore `signal-deck-orbital.html` reference from run artifacts or git history.
3. Phase 1: `orbital.css` + static shell matching frame 01.
4. Phase 2: API client + AppContext + one route (Deck).
5. Phase 3: remaining routes, e2e, Docker.
6. Decide whether Control Center lives in-repo or as a separate package to avoid bundle bloat.

**Non-goals for any revival unless explicitly scoped:**

- Cloud-hosted multi-tenant Control Center.
- Replacing Cursor Task as the executor.
- Real-time Cursor token telemetry without an official API.

---
