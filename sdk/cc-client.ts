/**
 * Thin HTTP helpers for Control Center APIs (atlas-dev).
 * Ingest posts delegate to ingest-client.ts for mapping and redaction.
 */
import {
  ingestClientFromEnv,
  redactSecrets,
  type IngestEvent,
  type ActivityKind,
} from "./ingest-client.js";

export type IngestKind = ActivityKind;
export type { IngestEvent };
export { redactSecrets };

export function ccConfigured(): boolean {
  return Boolean(process.env.ATLAS_CC_URL && process.env.ATLAS_CC_TOKEN);
}

/** Fire-and-forget ingest; returns false when CC env is unset or POST fails. */
export async function postIngest(event: IngestEvent): Promise<boolean> {
  const client = ingestClientFromEnv(event.runId);
  if (!client) return false;
  await client.post(event);
  return true;
}

export async function ccFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const base = process.env.ATLAS_CC_URL?.replace(/\/$/, "");
  const token = process.env.ATLAS_CC_TOKEN;
  if (!base || !token) throw new Error("ATLAS_CC_URL and ATLAS_CC_TOKEN required");
  return fetch(`${base}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Atlas-CC-Token": token,
      ...(init.headers as Record<string, string> | undefined),
    },
  });
}
