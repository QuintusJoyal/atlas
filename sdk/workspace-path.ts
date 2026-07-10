/** Host ↔ container workspace prefix mapping for multi-workspace runners. */

export interface PathMapping {
  hostPrefix: string;
  containerPrefix: string;
}

/** Normalize path separators and trim trailing slashes (except root). */
export function normalizePath(p: string): string {
  const n = p.replace(/\\/g, '/').replace(/\/+/g, '/');
  if (n.length > 1 && n.endsWith('/')) return n.slice(0, -1);
  return n || '/';
}

function parsePairSegment(segment: string): PathMapping | null {
  const trimmed = segment.trim();
  if (!trimmed) return null;
  const slash = trimmed.replace(/\\/g, '/');
  const win = /^([A-Za-z]:[/].*?):(\/.*)$/.exec(slash);
  if (win) {
    return { hostPrefix: normalizePath(win[1]), containerPrefix: normalizePath(win[2]) };
  }
  const unix = /^(.+?):(\/.*)$/.exec(slash);
  if (unix) {
    return { hostPrefix: normalizePath(unix[1]), containerPrefix: normalizePath(unix[2]) };
  }
  return null;
}

/** Parse `ATLAS_PATH_MAP`: JSON object/array or comma-separated `host:container` pairs. */
export function parsePathMap(raw?: string): PathMapping[] {
  if (!raw?.trim()) return [];
  const trimmed = raw.trim();
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      const parsed = JSON.parse(trimmed) as unknown;
      const out: PathMapping[] = [];
      if (Array.isArray(parsed)) {
        for (const item of parsed) {
          if (item && typeof item === 'object') {
            const host = (item as { host?: unknown; hostPrefix?: unknown }).host
              ?? (item as { hostPrefix?: unknown }).hostPrefix;
            const container = (item as { container?: unknown; containerPrefix?: unknown }).container
              ?? (item as { containerPrefix?: unknown }).containerPrefix;
            if (typeof host === 'string' && typeof container === 'string') {
              out.push({ hostPrefix: normalizePath(host), containerPrefix: normalizePath(container) });
            }
          }
        }
      } else if (parsed && typeof parsed === 'object') {
        for (const [host, container] of Object.entries(parsed)) {
          if (typeof container === 'string') {
            out.push({ hostPrefix: normalizePath(host), containerPrefix: normalizePath(container) });
          }
        }
      }
      return sortMappings(out);
    } catch {
      return [];
    }
  }
  return sortMappings(
    trimmed
      .split(',')
      .map(parsePairSegment)
      .filter((m): m is PathMapping => m !== null),
  );
}

function sortMappings(mappings: PathMapping[]): PathMapping[] {
  return [...mappings].sort((a, b) => b.hostPrefix.length - a.hostPrefix.length);
}

function workspaceMounts(env: NodeJS.ProcessEnv): string[] {
  const raw =
    env.ATLAS_WORKSPACE_MOUNTS || env.ATLAS_WORKSPACE || env.ATLAS_ROOT || '';
  return raw
    .split(',')
    .map((s) => normalizePath(s.trim()))
    .filter(Boolean);
}

/** Build path mappings from env (explicit map, or ATLAS_WORKSPACE_HOST + ATLAS_WORKSPACE). */
export function pathMappingsFromEnv(env: NodeJS.ProcessEnv = process.env): PathMapping[] {
  const explicit = parsePathMap(env.ATLAS_PATH_MAP);
  if (explicit.length) return explicit;

  const host = env.ATLAS_WORKSPACE_HOST?.trim();
  const container = env.ATLAS_WORKSPACE || env.ATLAS_ROOT;
  if (host && container) {
    return [{ hostPrefix: normalizePath(host), containerPrefix: normalizePath(container) }];
  }
  return [];
}

/**
 * Map run `meta.workspace` (often a host path) to the cwd the SDK runner should use.
 * Falls back to ATLAS_WORKSPACE, then ATLAS_ROOT, then process.cwd() when meta is empty.
 */
export function resolveWorkspaceCwd(
  metaWorkspace: string,
  env: NodeJS.ProcessEnv = process.env,
  options?: { pathMap?: PathMapping[]; fallback?: string },
): string {
  const fallback = normalizePath(
    options?.fallback ?? env.ATLAS_WORKSPACE ?? env.ATLAS_ROOT ?? process.cwd(),
  );
  const ws = metaWorkspace?.trim();
  if (!ws) return fallback;

  const normalized = normalizePath(ws);
  const mounts = workspaceMounts(env);
  if (mounts.includes(normalized)) return normalized;

  const mappings = options?.pathMap?.length ? sortMappings(options.pathMap) : pathMappingsFromEnv(env);
  for (const { hostPrefix, containerPrefix } of mappings) {
    const hostNorm = normalizePath(hostPrefix);
    if (normalized === hostNorm) return normalizePath(containerPrefix);
    const prefixWithSlash = hostNorm.endsWith('/') ? hostNorm : `${hostNorm}/`;
    if (normalized.startsWith(prefixWithSlash)) {
      const suffix = normalized.slice(hostNorm.length);
      return normalizePath(`${containerPrefix}${suffix.startsWith('/') ? suffix : `/${suffix}`}`);
    }
  }

  const workspace = env.ATLAS_WORKSPACE ? normalizePath(env.ATLAS_WORKSPACE) : undefined;
  const root = env.ATLAS_ROOT ? normalizePath(env.ATLAS_ROOT) : undefined;
  if (workspace && normalized === workspace) return workspace;
  if (root && normalized === root) return root;

  const looksLikeHostPath = /^[A-Za-z]:[/\\]/.test(ws) || ws.startsWith('\\\\');
  const runnerInContainer = mounts.some((m) => m.startsWith('/'));
  if (looksLikeHostPath && runnerInContainer && mappings.length === 0) {
    return fallback;
  }

  return normalized;
}
