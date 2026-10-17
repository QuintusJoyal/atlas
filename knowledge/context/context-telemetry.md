---
name: context-telemetry
category: context
load-when: Reviewing run token usage, auditing context quality after a run, exporting Atlas metrics, tuning context budgets
skip-when: Normal operation, simple tasks
description: Post-hoc context telemetry over trajectory.jsonl — token accounting, cache hit rate, compaction logging, poisoning/distraction/confusion/clash detection, and OTel-shaped export of the 8 Atlas metrics.
audience: [atlas-lead, atlas-ai-eng, atlas-ent-arch]
tags: [telemetry, tokens, poisoning, cache, compaction, otel, metrics, budget]
---

# Context telemetry and poisoning detection

This bundle has no runtime, so "real-time" collection is the host IDE's job (see `knowledge/process/runtime-execution.md`); what this bundle owns is the **event schema, the definitions, and the analyzer**. IDEs append telemetry events to the existing trajectory log (`knowledge/process/trajectory-logging.md`); `scripts/context-telemetry.py` computes the metrics after a run and emits an OTel-compatible export. No numbers here are precise measurements — token counts are estimates, and the quality detectors are deterministic heuristics that flag *candidates* for review, never verdicts.

## Quick Reference
- Extend `trajectory.jsonl` with three optional event types: `cache`, `compaction`, `context`
- 4 context failure modes: poisoning, distraction, confusion, clash — each with severity low/medium/high
- Budget categories: `inline`, `search`, `load` (matches how context enters the window)
- Analyzer: `python3 scripts/context-telemetry.py <run-dir|trajectory.jsonl>`
- Formats: `dashboard` (default), `flags`, `metrics`, `otel`, `json`

## Telemetry event extensions

Telemetry rides on the existing trajectory schema as new entry types selected by an optional `event` field. Entries without `event` are ordinary decision points and are analyzed as-is.

### `event: "cache"` — prompt cache utilization

| Field | Required | Description |
|-------|----------|-------------|
| `boundary` | yes | `static` (system prompt, rules, playbooks) or `dynamic` (task context, tool output) |
| `hit` | yes | true = cache hit, false = miss |
| `tokens` | yes | Tokens served from (hit) or re-sent (miss) |

Cache hit rate = hits / total, reported separately per boundary. The static boundary is expected to be near 1.0; a low static hit rate means the bundle's load-when gating or prompt ordering is defeating the IDE's cache.

### `event: "compaction"` — context compaction log

| Field | Required | Description |
|-------|----------|-------------|
| `trigger` | yes | `manual`, `budget`, or `threshold` |
| `tokensBefore` | yes | Context tokens immediately before compaction |
| `tokensAfter` | yes | Context tokens immediately after |
| `qualityScore` | no | Host IDE's 0–1 estimate of summarization quality |
| `summary` | no | What was compacted away |

The analyzer reports every compaction: trigger, context delta (`tokensAfter - tokensBefore`), and the average `qualityScore`. Compactions with `qualityScore` < 0.6 or a delta over 80% of `tokensBefore` (most of the context discarded) are flagged as low-quality compactions.

### `event: "context"` — category accounting

| Field | Required | Description |
|-------|----------|-------------|
| `category` | yes | How the tokens entered the window: `inline` (prompt/handoff), `search` (grep/glob results), `load` (file reads, knowledge loads) |
| `tokens` | yes | Tokens added |

Decision entries may also carry an optional `contextCategory` with the same values; if present it is counted even without a `context` event.

### Optional fields on decision entries

| Field | Description |
|-------|-------------|
| `phase` | Workflow phase (requirements, design, implementation, test, review) — enables per-phase accounting |
| `expectedTokens` | Lead's predicted tokens for this decision — enables REI |
| `durationMs` | Wall time of the decision — enables PER |
| `tier` | Model tier used (premium, standard, fast) — enables MTAS |

## Context failure modes and severity

Detectors are deterministic heuristics over trajectory fields. Each flag carries `type`, `severity`, `role`, `target`, and `evidence`. A flag is a review candidate, not a verdict.

### Poisoning — hallucinated content propagated as fact
A failed claim reappears as accepted context: an entry with `outcome=failure` (typically `errorCategory` validation or business) whose `error` text (≥ 20 chars, normalized) is found in the `why`, `approach`, or `toolOutput` of a **later, successful** entry. The failed information is now in context as if it were true.
Severity: high (any match). This is the most dangerous mode — it silently corrupts everything downstream.

### Distraction — volume exceeding effective attention
Cumulative tokens in a phase exceed the phase budget (default 40,000; override with `--phase-budget`).
Severity: low ≥ 1× budget, medium ≥ 1.5×, high ≥ 2×.

### Confusion — re-derivation of already-provided context
The same role reads the same target ≥ 3 times with no intervening edit to that target by that role: the information was in context but not retained or not recognized as relevant.
Severity: low 3–4 reads, medium 5–6, high ≥ 7.

### Clash — conflicting information in context
The same role applies ≥ 2 distinct `approach` values to the same target, or a successful edit is followed by a failure on the same target with a different approach: two incompatible facts about the same thing are in context.
Severity: low 2 approaches, medium 3, high ≥ 4 or any success→failure inversion.

## The 8 multi-agent metrics

`scripts/context-telemetry.py --format metrics|otel` computes the metrics defined in `knowledge/process/observability-system.md` from trajectory data. Metrics whose inputs nobody logged come back as `null` with a reason — never as a fabricated number.

| Metric | Needs | Fallback |
|--------|-------|----------|
| IAHQS, DAS | `action: delegate` entries + delegated role's next outcome | — |
| EJR | `action: escalate` entries | — |
| GYR | `action: gate-check` entries grouped by `target` | — |
| REI | `expectedTokens` on decisions | null if absent |
| CPS | confusion flags (re-reads) + delegations | — |
| PER | `durationMs` on entries | null if absent |
| MTAS | `tier` per entry + a role→expected-tier map (`--tier-map role=tier,...`) | null if absent |

## OTel export shape

`--format otel` prints a single JSON document shaped for an OTel metrics pipeline (OTLP/JSON-compatible field names). The host IDE or a collector can forward it; nothing in this bundle ships a collector.

```json
{
  "resource": { "service.name": "atlas", "atlas.run.id": "<run-id>" },
  "metrics": [
    { "name": "atlas.context.tokens.total", "unit": "By", "sum": 128400,
      "attributes": { "atlas.role": "atlas-dev", "atlas.phase": "implementation" } },
    { "name": "atlas.context.cache.hit_ratio", "unit": "1", "gauge": 0.92,
      "attributes": { "atlas.cache.boundary": "static" } },
    { "name": "atlas.context.quality.flags", "unit": "1", "sum": 2,
      "attributes": { "atlas.quality.type": "poisoning", "atlas.quality.severity": "high" } },
    { "name": "atlas.metric.iahqs", "unit": "1", "gauge": 0.94 }
  ]
}
```

Metric names: `atlas.context.tokens.total`, `atlas.context.cache.hit_ratio`, `atlas.context.compaction.count`, `atlas.context.compaction.delta` (By), `atlas.context.quality.flags`, plus `atlas.metric.<iahqs|das|ejr|gyr|rei|cps|per|mtas>`.

## Integration

- **Budgets:** the per-role/per-phase totals feed the budget checks in `knowledge/process/dashboard-spec.md` and the Budget Bleed anomaly in `knowledge/process/observability-system.md`.
- **Stuck-agent detection:** a role whose flags accumulate (repeated confusion on the same target, or distraction at high severity) with no outcome progression is a stuck-agent signal for atlas-lead — the analyzer's `flags` format is the cheap input for that check.
- **Poisoning defense:** treat a high-severity poisoning flag as a pre-handoff gate failure per `knowledge/context/pre-handoff-quality-check.md` — the offending context must be corrected before the next delegation.

## Usage

```bash
# Human dashboard for one run
python3 scripts/context-telemetry.py ~/.atlas/data/runs/<run-id>/trajectory.jsonl

# Quality flags only (exit 1 if any high-severity flag — usable as a gate)
python3 scripts/context-telemetry.py trajectory.jsonl --format flags --fail-on high

# OTel export with a 30K phase budget and tier map
python3 scripts/context-telemetry.py trajectory.jsonl --format otel \
  --phase-budget 30000 --tier-map atlas-lead=premium,atlas-dev=standard
```

Token counts use the `tokens`/`tokensEstimate` fields when present and fall back to a chars/4 heuristic; if the optional `tiktoken` package is installed it is used for the fallback instead. Every report states which method was used.
