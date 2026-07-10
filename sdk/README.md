# Atlas SDK orchestrator (optional)

Headless pipeline runner and Control Center job worker, built on the Cursor SDK. Runs in Docker by default alongside Control Center; host `npm install` is deprecated.

## Docker (default)

From sibling **`../atlas-control-center/`** (or `C:/Users/you/Projects/atlas-control-center/`):

```bash
cp .env.example .env
# ATLAS_HOME: user home (Windows: C:/Users/you; macOS/Linux: /Users/you)
# ATLAS_WORKSPACE_HOST: absolute path to any code workspace (e.g. ../atlas or your app repo)
# ATLAS_KB_HOST: knowledge base on host (dev: ../atlas/knowledge; prod: ~/.cursor/atlas-knowledge)
# ATLAS_CC_TOKEN and CURSOR_API_KEY (runner only; never on control-center)

docker compose up -d --build
```

Compose binds `$ATLAS_HOME/.cursor/atlas-data` (central Atlas home), `${ATLAS_WORKSPACE_HOST}` at `/workspace`, and `${ATLAS_KB_HOST}` at `/kb`. No `docker-compose.override.yml` is required when `.env` is set.

The `sdk-runner` service:

- Builds from this directory (`../atlas/sdk` relative to `atlas-control-center/`).
- Runs `npm run runner` inside the image (deps installed at build time).
- Connects to Control Center at `http://control-center:3847` on the Compose network.
- Holds `CURSOR_API_KEY`; Control Center stays keyless.
- Shares the same volumes as Control Center (`ATLAS_DATA_DIR=/atlas-data`, `ATLAS_WORKSPACE=/workspace`).

### Runner workspace resolution

Pipeline and ticket jobs execute agents in the run's `meta.workspace`, mapped to a container path when the runner is in Docker:

- **`ATLAS_PATH_MAP`**: JSON (`{"C:/host/repo":"/workspace"}`) or comma-separated pairs (`C:/host/repo:/workspace`). Longest host prefix wins.
- **`ATLAS_WORKSPACE_HOST` + `ATLAS_WORKSPACE`**: auto-derives a single map when `ATLAS_PATH_MAP` is unset.
- **`ATLAS_WORKSPACE_MOUNTS`**: if `meta.workspace` already matches a mount entry, it is used as-is.
- **Fallback**: `ATLAS_WORKSPACE`, then `ATLAS_ROOT`, then `process.cwd()` when meta is missing (legacy runs).

`GET /api/session` returns `pathMap` hints; `pipeline.run` jobs include `workspace` and `pathMap` in the payload.

Verify: `GET http://localhost:3847/api/session` should show `runnerConnected: true`.

## Orchestrator (CI / one-off)

For a single headless pipeline run (not the long-lived runner), exec into the runner container or run a one-off from `atlas-control-center/`:

```bash
docker compose run --rm sdk-runner npm run pipeline -- "add CSV export to the reports page"
```

Requires `CURSOR_API_KEY`, `ATLAS_CC_URL`, and `ATLAS_CC_TOKEN` (set via compose for the runner service).

When `ATLAS_CC_URL` and `ATLAS_CC_TOKEN` are set, the orchestrator posts pipeline telemetry to Control Center `POST /api/events/ingest`. Stream and Deck show live agent, gate, and budget events.

Optional: `ATLAS_RUN_ID` for run correlation. See `ingest-client.ts` for event mapping from `run.stream()`.

The orchestrator runs phases in sequence (requirements, design, implementation, test, review, security), threading each phase's output into the next. Approval gates surface as console prompts; in unattended mode (`ATLAS_UNATTENDED=1`) it stops at the first gate.

## Host install (deprecated)

Host-side `npm install` is no longer supported for normal operation. All npm dependencies live inside Docker images. If you must run locally for SDK development, use an isolated environment and do not commit `node_modules/`.

## Notes

- The SDK surface evolves. See https://cursor.com/docs/sdk/typescript for the reference.
- Extend `orchestrator.ts` / `runner.ts` for your CI or automation needs.
