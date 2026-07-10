import { CursorAgentError } from "@cursor/sdk";

/** SDK-valid slugs from Cursor.models.list(); used at Agent.create runtime. */
export const TIER_MODELS = {
  premium: "claude-opus-4-8",
  standard: "composer-2.5",
  fast: "composer-2",
} as const;

export const MODEL_CASCADE = [
  TIER_MODELS.premium,
  TIER_MODELS.standard,
  TIER_MODELS.fast,
  "default",
] as const;

export type CascadeModel = (typeof MODEL_CASCADE)[number];

/**
 * IDE Task/subagent and agent frontmatter slugs that are not accepted by the SDK.
 * Map to Cursor.models.list() ids before Agent.create.
 */
const LEGACY_MODEL_ALIASES: Record<string, string> = {
  "composer-2.5-fast": TIER_MODELS.standard,
  "claude-opus-4-8-thinking-high": TIER_MODELS.premium,
  "claude-opus-4-7-thinking-medium": "claude-opus-4-7",
};

export function resolveModel(preferred: string): string {
  return LEGACY_MODEL_ALIASES[preferred] ?? preferred;
}

export function roleTierToModel(tier?: string): string {
  if (tier === "premium") return TIER_MODELS.premium;
  if (tier === "fast") return TIER_MODELS.fast;
  return TIER_MODELS.standard;
}

export function modelFallbackChain(preferred: string): string[] {
  const resolved = resolveModel(preferred);
  if (resolved === "inherit" || preferred === "inherit") {
    return ["default"];
  }
  const idx = (MODEL_CASCADE as readonly string[]).indexOf(resolved);
  if (idx >= 0) {
    return [...MODEL_CASCADE.slice(idx)];
  }
  return [resolved, ...MODEL_CASCADE.slice(1)];
}

export function isModelUnavailableError(err: unknown): boolean {
  if (err instanceof CursorAgentError) {
    const msg = (err.message || "").toLowerCase();
    return (
      err.isRetryable ||
      msg.includes("cannot use this model") ||
      msg.includes("quota") ||
      msg.includes("rate limit") ||
      msg.includes("rate-limit") ||
      msg.includes("unavailable") ||
      msg.includes("not available") ||
      msg.includes("blocked") ||
      msg.includes("permission")
    );
  }
  const msg = (err instanceof Error ? err.message : String(err)).toLowerCase();
  return (
    msg.includes("cannot use this model") ||
    msg.includes("quota") ||
    msg.includes("rate limit") ||
    msg.includes("rate-limit") ||
    msg.includes("unavailable") ||
    msg.includes("not available") ||
    msg.includes("blocked") ||
    msg.includes("permission")
  );
}
