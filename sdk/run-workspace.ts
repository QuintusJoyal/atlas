import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { ccFetch } from "./cc-client.js";
import {
  resolveWorkspaceCwd,
  type PathMapping,
} from "./workspace-path.js";

function parsePayloadPathMap(raw: unknown): PathMapping[] | undefined {
  if (!Array.isArray(raw)) return undefined;
  const out: PathMapping[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const hostPrefix = (item as { hostPrefix?: unknown }).hostPrefix;
    const containerPrefix = (item as { containerPrefix?: unknown }).containerPrefix;
    if (typeof hostPrefix === "string" && typeof containerPrefix === "string") {
      out.push({ hostPrefix, containerPrefix });
    }
  }
  return out.length ? out : undefined;
}

/** Load meta.workspace from CC API or ATLAS_DATA_DIR. */
export async function fetchRunWorkspace(runId: string): Promise<string | undefined> {
  try {
    const res = await ccFetch(`/api/runs/${runId}/state`);
    if (res.ok) {
      const state = (await res.json()) as { workspace?: string };
      const ws = state.workspace?.trim();
      if (ws) return ws;
    }
  } catch {
    /* fall through to disk */
  }

  const dataDir = process.env.ATLAS_DATA_DIR?.trim();
  if (!dataDir) return undefined;
  const metaPath = join(dataDir, "runs", runId, "meta.json");
  if (!existsSync(metaPath)) return undefined;
  try {
    const meta = JSON.parse(readFileSync(metaPath, "utf8")) as { workspace?: string };
    return typeof meta.workspace === "string" ? meta.workspace.trim() || undefined : undefined;
  } catch {
    return undefined;
  }
}

export async function resolveCwdForRun(
  runId: string | undefined,
  payload?: Record<string, unknown>,
): Promise<string> {
  const payloadWorkspace =
    typeof payload?.workspace === "string" ? payload.workspace.trim() : undefined;
  const pathMap = parsePayloadPathMap(payload?.pathMap);
  const metaWorkspace =
    payloadWorkspace || (runId ? await fetchRunWorkspace(runId) : undefined) || "";
  return resolveWorkspaceCwd(metaWorkspace, process.env, { pathMap });
}
