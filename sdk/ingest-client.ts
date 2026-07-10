/**
 * Control Center ingest client for the host SDK runner and orchestrator.
 * Posts telemetry to POST /api/events/ingest; maps run.stream() SDKMessage events
 * to IngestEvent kinds. Contract mirrors atlas-control-center/shared/types.ts.
 *
 * Env: ATLAS_CC_URL, ATLAS_CC_TOKEN (optional). When unset, all calls no-op.
 */

/** Mirrors ActivityKind in atlas-control-center/shared/types.ts */
export type ActivityKind = "agent" | "gate" | "file" | "budget" | "ticket" | "system";

export interface IngestEvent {
  kind: ActivityKind;
  runId?: string;
  actor?: string;
  message: string;
  ts?: string;
  meta?: Record<string, unknown>;
}

/** Minimal SDKMessage shape from @cursor/sdk run.stream() (see SDK docs). */
export interface SdkStreamEvent {
  type: string;
  agent_id?: string;
  run_id?: string;
  message?: {
    role?: string;
    content?: Array<{ type: string; text?: string; name?: string; id?: string; input?: unknown }>;
  };
  text?: string;
  call_id?: string;
  name?: string;
  status?: string;
  args?: unknown;
  result?: unknown;
  request_id?: string;
  subtype?: string;
  model?: unknown;
}

export interface IngestClientOptions {
  baseUrl: string;
  token: string;
  runId?: string;
  /** Max chars per batched assistant line (default 480). */
  maxMessageLen?: number;
  /** Batch window for assistant stream chunks in ms (default 500). */
  batchMs?: number;
}

const SECRET_PATTERNS = [
  /cursor_[a-zA-Z0-9_-]{10,}/gi,
  /Bearer\s+[a-zA-Z0-9._-]+/gi,
  /ATLAS_CC_TOKEN[=:]\s*\S+/gi,
  /CURSOR_API_KEY[=:]\s*\S+/gi,
];

export function redactSecrets(text: string): string {
  let out = text;
  for (const re of SECRET_PATTERNS) {
    out = out.replace(re, "[redacted]");
  }
  return out;
}

function truncate(text: string, max: number): string {
  const t = text.trim();
  if (t.length <= max) return t;
  return t.slice(0, max - 1) + "…";
}

/** Build client from env; returns null when CC URL/token are not configured. */
export function ingestClientFromEnv(runId?: string): IngestClient | null {
  const baseUrl = (process.env.ATLAS_CC_URL || "").replace(/\/$/, "");
  const token = process.env.ATLAS_CC_TOKEN || "";
  if (!baseUrl || !token) return null;
  const id = runId || process.env.ATLAS_RUN_ID;
  return new IngestClient({ baseUrl, token, runId: id });
}

export class IngestClient {
  private readonly baseUrl: string;
  private readonly token: string;
  readonly runId?: string;
  private readonly maxMessageLen: number;
  private readonly batchMs: number;

  constructor(opts: IngestClientOptions) {
    this.baseUrl = opts.baseUrl.replace(/\/$/, "");
    this.token = opts.token;
    this.runId = opts.runId;
    this.maxMessageLen = opts.maxMessageLen ?? 480;
    this.batchMs = opts.batchMs ?? 500;
  }

  /** Fire-and-forget POST; logs warning on failure, never throws. */
  async post(event: IngestEvent): Promise<void> {
    const body: IngestEvent = {
      ...event,
      message: redactSecrets(event.message),
      runId: event.runId ?? this.runId,
      ts: event.ts ?? new Date().toISOString(),
    };
    try {
      const res = await fetch(`${this.baseUrl}/api/events/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Atlas-CC-Token": this.token,
        },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        console.warn(`[ingest] POST failed: ${res.status} ${res.statusText}`);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn(`[ingest] POST error: ${msg}`);
    }
  }

  phaseStart(actor: string, phase?: string, meta?: Record<string, unknown>): Promise<void> {
    const label = phase ? `started ${phase} phase` : "started phase";
    return this.post({
      kind: "agent",
      actor,
      message: `${actor}: ${label}`,
      meta: { signal: "phase.start", phase, ...meta },
    });
  }

  phaseComplete(actor: string, tier: string, meta?: Record<string, unknown>): Promise<void> {
    return this.post({
      kind: "agent",
      actor,
      message: `${actor}: completed (${tier})`,
      meta: { signal: "phase.complete", tier, ...meta },
    });
  }

  /** Model downgrade / token-budget self-report line. */
  budget(message: string, actor?: string, meta?: Record<string, unknown>): Promise<void> {
    return this.post({
      kind: "budget",
      actor,
      message: redactSecrets(message),
      meta: { signal: "budget", ...meta },
    });
  }

  downgrade(actor: string, fromTier: string, toTier: string, reason = "quota-or-unavailable"): Promise<void> {
    const line = `downgrade: ${actor} ${fromTier} → ${toTier}, reason ${reason}`;
    return this.budget(line, actor, { signal: "downgrade", fromTier, toTier, reason });
  }

  gatePause(gate: string, actor = "atlas-lead"): Promise<void> {
    return this.post({
      kind: "gate",
      actor,
      message: `gate ${gate}: awaiting approval`,
      meta: { signal: "gate.pause", gate },
    });
  }

  fileWrite(actor: string, filename: string, meta?: Record<string, unknown>): Promise<void> {
    return this.post({
      kind: "file",
      actor,
      message: `wrote ${filename}`,
      meta: { signal: "file.write", filename, ...meta },
    });
  }

  ticket(actor: string, message: string, meta?: Record<string, unknown>): Promise<void> {
    return this.post({
      kind: "ticket",
      actor,
      message: redactSecrets(message),
      meta: { signal: "ticket", ...meta },
    });
  }

  system(message: string, meta?: Record<string, unknown>): Promise<void> {
    return this.post({
      kind: "system",
      message: redactSecrets(message),
      meta: { signal: "system", ...meta },
    });
  }

  kickoff(workflow: string, runId: string): Promise<void> {
    return this.system(`kickoff: ${workflow} run ${runId} created`, {
      signal: "kickoff",
      workflow,
      runId,
    });
  }

  /** Batches assistant stream text before posting agent ingest lines. */
  streamMapper(actor: string, runId?: string): StreamIngestMapper {
    return new StreamIngestMapper(this, {
      actor,
      runId: runId ?? this.runId,
      maxMessageLen: this.maxMessageLen,
      batchMs: this.batchMs,
    });
  }
}

export interface StreamMapperContext {
  actor: string;
  runId?: string;
  maxMessageLen: number;
  batchMs: number;
}

const FILE_TOOL_NAMES = new Set([
  "write",
  "strreplace",
  "search_replace",
  "edit",
  "delete",
  "writefile",
]);

function isFileTool(name: string): boolean {
  const n = name.toLowerCase().replace(/[^a-z]/g, "");
  return FILE_TOOL_NAMES.has(n) || n.includes("write") || n.includes("edit");
}

function extractAssistantText(event: SdkStreamEvent): string {
  const parts: string[] = [];
  for (const block of event.message?.content ?? []) {
    if (block.type === "text" && block.text) parts.push(block.text);
  }
  return parts.join("");
}

function inferFilenameFromTool(name: string, args: unknown): string | undefined {
  if (!args || typeof args !== "object") return undefined;
  const a = args as Record<string, unknown>;
  if (typeof a.path === "string") return a.path.split(/[/\\]/).pop();
  if (typeof a.file_path === "string") return a.file_path.split(/[/\\]/).pop();
  if (typeof a.filename === "string") return a.filename;
  return name;
}

/**
 * Maps run.stream() SDKMessage events to ingest posts.
 * Assistant text is batched; tool/file/status/request events flush the buffer first.
 */
export class StreamIngestMapper {
  private buffer = "";
  private timer: ReturnType<typeof setTimeout> | null = null;
  private readonly ctx: StreamMapperContext;

  constructor(
    private readonly client: IngestClient,
    ctx: Partial<StreamMapperContext> & { actor: string },
  ) {
    this.ctx = {
      actor: ctx.actor,
      runId: ctx.runId,
      maxMessageLen: ctx.maxMessageLen ?? 480,
      batchMs: ctx.batchMs ?? 500,
    };
  }

  async onEvent(event: SdkStreamEvent): Promise<void> {
    const meta = {
      sdkRunId: event.run_id,
      sdkAgentId: event.agent_id,
      sdkType: event.type,
    };

    switch (event.type) {
      case "assistant": {
        const text = extractAssistantText(event);
        if (text) this.appendAssistant(text);
        return;
      }
      case "tool_call": {
        await this.flush();
        const toolName = event.name ?? "tool";
        if (event.status === "completed" && isFileTool(toolName)) {
          const file = inferFilenameFromTool(toolName, event.args ?? event.result);
          if (file) {
            await this.client.fileWrite(this.ctx.actor, file, meta);
            return;
          }
        }
        const status = event.status ?? "running";
        await this.client.post({
          kind: "agent",
          actor: this.ctx.actor,
          runId: this.ctx.runId,
          message: truncate(`${this.ctx.actor}: tool ${toolName} (${status})`, this.ctx.maxMessageLen),
          meta: { ...meta, toolName, toolStatus: status, callId: event.call_id },
        });
        return;
      }
      case "status": {
        if (event.status === "ERROR") {
          await this.flush();
          const detail =
            event.message != null && typeof event.message === "string" ? ` — ${event.message}` : "";
          await this.client.post({
            kind: "agent",
            actor: this.ctx.actor,
            runId: this.ctx.runId,
            message: truncate(`${this.ctx.actor}: run error${detail}`, this.ctx.maxMessageLen),
            meta: { ...meta, sdkStatus: event.status },
          });
        }
        return;
      }
      case "request": {
        await this.flush();
        await this.client.gatePause("approval", this.ctx.actor);
        return;
      }
      case "task": {
        if (event.text) {
          await this.flush();
          await this.client.post({
            kind: "agent",
            actor: this.ctx.actor,
            runId: this.ctx.runId,
            message: truncate(`${this.ctx.actor}: ${event.text}`, this.ctx.maxMessageLen),
            meta: { ...meta, taskStatus: event.status },
          });
        }
        return;
      }
      case "system": {
        if (event.subtype === "init") {
          await this.client.post({
            kind: "agent",
            actor: this.ctx.actor,
            runId: this.ctx.runId,
            message: `${this.ctx.actor}: run initialized`,
            meta: { ...meta, signal: "run.init" },
          });
        }
        return;
      }
      // user echo, thinking: skip (avoid SSE flood / noise)
      default:
        return;
    }
  }

  private appendAssistant(text: string): void {
    this.buffer += text;
    if (!this.timer) {
      this.timer = setTimeout(() => {
        void this.flush();
      }, this.ctx.batchMs);
    }
  }

  async flush(): Promise<void> {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    const raw = this.buffer.trim();
    this.buffer = "";
    if (!raw) return;
    await this.client.post({
      kind: "agent",
      actor: this.ctx.actor,
      runId: this.ctx.runId,
      message: truncate(raw, this.ctx.maxMessageLen),
      meta: { signal: "stream.chunk" },
    });
  }
}

/** Map a single SDK stream event to zero or more IngestEvent payloads (no HTTP). */
export function mapStreamEvent(
  event: SdkStreamEvent,
  ctx: { actor: string; runId?: string; maxMessageLen?: number },
): IngestEvent[] {
  const max = ctx.maxMessageLen ?? 480;
  const base = { runId: ctx.runId, actor: ctx.actor };
  const meta = { sdkRunId: event.run_id, sdkAgentId: event.agent_id, sdkType: event.type };
  const out: IngestEvent[] = [];

  switch (event.type) {
    case "assistant": {
      const text = extractAssistantText(event).trim();
      if (text) {
        out.push({
          kind: "agent",
          ...base,
          message: truncate(text, max),
          meta: { ...meta, signal: "stream.chunk" },
        });
      }
      break;
    }
    case "tool_call": {
      const toolName = event.name ?? "tool";
      if (event.status === "completed" && isFileTool(toolName)) {
        const file = inferFilenameFromTool(toolName, event.args ?? event.result);
        if (file) {
          out.push({
            kind: "file",
            ...base,
            message: `wrote ${file}`,
            meta: { ...meta, signal: "file.write", filename: file },
          });
          break;
        }
      }
      out.push({
        kind: "agent",
        ...base,
        message: truncate(`${ctx.actor}: tool ${toolName} (${event.status ?? "running"})`, max),
        meta: { ...meta, toolName, toolStatus: event.status },
      });
      break;
    }
    case "status":
      if (event.status === "ERROR") {
        out.push({
          kind: "agent",
          ...base,
          message: truncate(`${ctx.actor}: run error`, max),
          meta: { ...meta, sdkStatus: event.status },
        });
      }
      break;
    case "request":
      out.push({
        kind: "gate",
        actor: "atlas-lead",
        runId: ctx.runId,
        message: `gate approval: awaiting approval`,
        meta: { ...meta, signal: "gate.pause" },
      });
      break;
    case "task":
      if (event.text) {
        out.push({
          kind: "agent",
          ...base,
          message: truncate(`${ctx.actor}: ${event.text}`, max),
          meta: { ...meta, taskStatus: event.status },
        });
      }
      break;
    default:
      break;
  }
  return out;
}
