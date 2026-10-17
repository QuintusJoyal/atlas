---
name: context-freshness
category: process
load-when: Loading knowledge or handoff context, long-running runs, before incorporating prior artifacts
skip-when: Single-step tasks with no prior context
description: Treat context as perishable. Every loaded fragment carries a last-verified timestamp and TTL; stale fragments are warned, refreshed, or blocked.
audience: [all]
tags: [context, freshness, staleness, ttl, verification, provenance]
---

# Context freshness

Context is not just a token budget problem, it is a temporal one. A knowledge file, handoff artifact, or tool finding is a snapshot: it was true when it was loaded, not necessarily now. Atlas tracks that with explicit metadata and a gate before the fragment enters working memory. This changes WHEN a fragment is trusted, not WHAT is loaded.

Atlas has no runtime that enforces this gate. It is a convention every agent applies by hand. Treat it as a discipline, not a hard guarantee: a fragment with no freshness metadata is unknown, not automatically fresh.

## Quick Reference
- Fragment metadata: `loaded_at`, `source`, `source_mtime`, `max_staleness_hours`
- Gate: `now - source_mtime > max_staleness_hours` → the fragment is stale
- Three policies: `warn` (use + flag), `refresh` (re-load from disk), `block` (refuse + log)
- Phase TTLs: short for code/implementation (1h), longer for standards/planning (24h)
- Dashboard: list each fragment with fresh/stale/expired status and last verification
- Bootstrap checks `lessons.md` and knowledge files; stale items surface to the agent
- Cross-run: a run that used stale context is flagged in its run metadata

## Fragment schema

Every context fragment loaded into working memory carries these fields. For a knowledge file or handoff artifact they live in a `freshness` block, either in frontmatter or a fenced block at the top of the artifact:

```yaml
freshness:
  loaded_at: 2026-10-17T14:30:00Z      # when this agent read the fragment
  source: knowledge/context/codebase-context.md   # stable identifier / path
  source_mtime: 2026-10-17T09:00:00Z   # when the source was last verified or modified
  max_staleness_hours: 1               # TTL for this fragment in this phase
```

- `loaded_at` records provenance: which read, in which run.
- `source` is the path or identifier the fragment came from, so `refresh` knows what to re-read.
- `source_mtime` is the source's last-verified timestamp. Use the file mtime (`stat`) for disk files; for a handoff artifact use the time it was written.
- `max_staleness_hours` is the TTL. It comes from the phase TTL table below unless the fragment's own frontmatter pins a stricter one.

If a fragment has no metadata, record it as `unknown`: apply the current phase's default policy, which for `unknown` is always `warn`, never `block`.

## The freshness gate

Before a fragment is added to working memory, evaluate:

```
age_hours = now - source_mtime
stale = age_hours > max_staleness_hours
```

If `stale` is false, the fragment is **fresh**: load it, do nothing else. If true, check the age against twice the TTL:

- `age_hours <= 2 * max_staleness_hours` → **stale**
- `age_hours > 2 * max_staleness_hours` → **expired**

Then apply the phase policy for that status (see below). Run the gate once per fragment at load time, not on every reasoning turn.

### Caveat: long-running sessions

`source_mtime` does not change while a run is in flight unless the source is re-read. In a long run where the codebase changes underneath you, a fragment that was fresh at load can silently go stale. When a phase transitions, re-run the gate on the artifacts carried forward rather than trusting the earlier verdict. Don't re-check within a single reasoning chain; that produces noisy, contradictory warnings.

## Three policies

For the current phase and fragment status, apply exactly one policy:

### `warn`
Use the fragment, but append a one-line staleness warning next to where it is used:

```
[stale context] knowledge/context/codebase-context.md is 26h old (TTL 24h, source_mtime 2026-10-16T09:00Z). Verify before relying on it.
```

Log the warning to `trajectory.jsonl`. Default for planning and review phases, and always the fallback for `unknown` fragments.

### `refresh`
Re-load the fragment from `source` and reset `loaded_at` and `source_mtime` to now. This is for sources that *can* be re-read: disk files, grep results, MCP reads, handoff artifacts still on disk.

1. Re-read the source.
2. If it succeeds, replace the fragment, reset the timestamps, and continue as fresh.
3. If it fails (file gone, source unreachable), fall back to `warn` and note the failure. Never silently proceed as if refreshed.

Default for implementation and test phases, where the code or test state is expected to move.

### `block`
Refuse the fragment. Log an error with `errorCategory: stale-context`, `recoverable: true`, and a `suggestedAction` (refresh from source, or ask the user). If a fresh replacement cannot be found and the work depends on the fragment, escalate to atlas-lead rather than guessing.

Default for deploy and other irreversible/high-risk phases. Use `block` sparingly: a blocked fragment with no replacement stalls the phase.

## Per-phase TTL defaults

TTLs are shorter when the underlying truth moves fast (code, tests) and longer when it is stable (standards, references). This is the merge point: the phase sets the default, a fragment's own frontmatter can only tighten it, never loosen it.

| Phase category | Example phases | Default TTL | Default policy | Why |
|----------------|----------------|-------------|----------------|-----|
| Planning | requirements, design, discovery | 24h | warn | standards and references change slowly |
| Implementation | implement, fix, schema-change | 1h | refresh | code and API state move constantly |
| Test | test, verify | 2h | refresh | test results and fixtures can shift |
| Review | review, security-review | 4h | warn | review is point-in-time; flag, don't re-run silently |
| Deploy | deploy, migrate | 4h | block | irreversible steps must not act on stale state |

The canonical defaults live in `manifest.json` under `workflowMeta.freshness`. A workflow preset or fragment may narrow a TTL, but a stale-beyond-TTL fragment cannot be treated as fresh by asserting it is.

## Freshness dashboard (spec-only)

When the user asks for a context-freshness view, format it by hand as plain markdown (see `knowledge/process/dashboard-spec.md` for the general caveat: nothing renders this automatically). List every fragment used in the run:

```
Fragment                                   Source mtime          Age    TTL   Status   Policy
knowledge/context/codebase-context.md      2026-10-17T09:00Z     5h     1h    stale    refresh
knowledge/reference/lessons.md             2026-10-01T00:00Z     16d    24h   expired  warn
runs/run-.../design.md                     2026-10-17T13:00Z     1h     24h   fresh    -
```

- **fresh:** `age <= TTL`
- **stale:** `TTL < age <= 2*TTL`
- **expired:** `age > 2*TTL`

Include source, last verification time, and the policy applied. Fragments recorded as `unknown` are listed separately, not silently dropped.

## Bootstrap integration

The bootstrap step (see `rules/atlas-core.md`) greps `lessons.md` and `model-resilience.md` before any task. Treat those results as fragments:

1. Read the source file's mtime (or the last-verified date it records).
2. Compute `age` against the planning TTL (24h) at bootstrap.
3. For a stale lesson or knowledge file, surface it to the agent under a short `### Stale context` heading with the age and source, and apply `warn` (the bootstrap default). Never block at bootstrap — the run has not started yet.

This makes "this lesson is 6 months old" visible instead of implicit. A lesson that is repeatedly stale is a candidate for a knowledge-compounding proposal (see `knowledge/process/knowledge-compounding.md`), not an automatic deletion.

## Cross-run staleness tracking

When a run uses one or more stale or expired fragments, record it in the run's metadata at `$ATLAS_DATA_DIR/runs/<run-id>/` (for example `team.json` or a sibling `freshness.json`):

```json
{
  "runId": "run-20261017-central-data-home",
  "staleContext": [
    {"source": "knowledge/reference/lessons.md", "status": "expired", "policy": "warn", "age_hours": 384}
  ]
}
```

Post-hoc analysis (retrospective, `knowledge/process/knowledge-compounding.md`) reads this to ask whether a decision depended on stale context and whether the source should be refreshed more often. A run with no stale fragments records an empty list, so "clean" and "not tracked" are distinguishable.

## Anti-patterns

- Treating a bundled knowledge file as automatically fresh because it shipped with the bundle
- Blocking at bootstrap or on `unknown` fragments (stalls the run for no gain)
- Re-checking freshness on every reasoning turn instead of at load time and phase transitions
- Refreshing silently and hiding that the source had changed
- Using `refresh` on a source that cannot be re-read (a pasted finding, a live metric) and pretending it succeeded
- Marking a fragment fresh by editing its timestamp without re-reading the source

See `knowledge/context/context-engineering.md` for ordering and budget, `knowledge/context/memory-hierarchy.md` for which source wins on conflict, and `knowledge/context/pre-action-gates.md` for the freshness gate checklist.
