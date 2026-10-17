---
name: flight-recorder
category: process
load-when: Reproducing a failed run, debugging intermittent failures, building regression fixtures, verifying replay determinism
skip-when: Normal operation, single-pass tasks where a cheap re-run answers the question
description: Deterministic record/replay protocol. Capture every model, tool, retrieval, and environment exchange at the transport boundary into a run cassette; replay it offline with zero outbound network.
audience: [atlas-lead, atlas-ai-eng, all]
tags: [replay, determinism, cassette, flight-recorder, debugging, fixtures]
---

# Flight recorder (deterministic record and replay)

Atlas runs were previously unreplayable: trajectory logging captures decisions, observability captures live traces, and checkpoint-fork "replay" re-runs with live sampling, so LLM variance and external API state make every re-run different. The flight recorder captures the full input/output of every exchange at the transport boundary, then serves those exchanges back during replay so a run reproduces exactly. Related research: deterministic replay for AI agent systems (arXiv:2607.16200).

## Quick Reference
- Capture at the transport boundary: model requests/responses, tool calls, retrievals, environment reads
- One append-only cassette per run: `$ATLAS_DATA_DIR/runs/<run-id>/cassette.jsonl`
- Replay invariant: replay performs zero outbound network calls; an uncaptured exchange aborts replay, it never falls through to live
- Determinism invariant: same cassette + same agent code yields byte-identical trajectory decisions and tool inputs after noise normalization; model outputs are served from the cassette, never resampled
- Noise-aware diff: timestamps, headers, and latency are classified as noise before two cassettes are compared; only signal differences count as divergence
- Lite mode: record and replay model and tool I/O only
- Fixtures: exported, hash-pinned cassettes are the regression inputs for the golden-task eval harness (issue #40)

## Capture points

Recording hooks sit at the transport boundary, below agent logic, so nothing the agent sees escapes the cassette.

| Exchange kind | Hook point | Captured |
|---------------|-----------|----------|
| `model` | model client, before send / after receive | full messages, parameters (temperature, seed, tools), full response |
| `tool` | tool dispatcher, before invoke / after return | tool name, full arguments, full result or structured error |
| `retrieval` | knowledge fetch, MCP read, RAG query | query, source identifier, full returned fragments |
| `env` | environment reads that influence decisions | variable names and values, clock snapshot, working directory |

Rules:
- Capture the payload verbatim. Summaries belong in the trajectory, not the cassette.
- Capture is fail-closed: if recording is on and the capture write fails, the exchange fails too. A half-recorded run must not masquerade as reproducible.
- Redact secrets at capture time (replace value, keep name and a content hash). A cassette must be safe to attach to a bug report; replay of a redacted secret requires re-supplying it out of band.

## Cassette schema

Cassette is JSONL: one entry per exchange, ordered, append-only, gapless `seq`.

| Field | Required | Description |
|-------|----------|-------------|
| `seq` | yes | Gapless integer, 1-based. Replay lookup key. |
| `ts` | yes | ISO 8601 capture time. Noise-classified. |
| `kind` | yes | `model`, `tool`, `retrieval`, `env` |
| `role` | yes | Agent role that initiated the exchange |
| `request` | yes | Full outbound payload, verbatim |
| `response` | yes | Full inbound payload, verbatim (or structured error object) |
| `responseHash` | yes | SHA-256 of the canonicalized response. Fixture pin. |
| `meta` | no | `latencyMs`, request IDs, headers, `httpStatus`. Noise-classified: excluded from fixture export and from signal diffs. |

```jsonl
{"seq":1,"ts":"2026-10-12T18:33:32Z","kind":"model","role":"atlas-dev","request":{"messages":[{"role":"user","content":"Fix the N+1 query"}],"temperature":0.2,"seed":42},"response":{"content":"Batch with Promise.all","usage":{"totalTokens":1200}},"responseHash":"9f2c…","meta":{"latencyMs":840,"requestId":"req_8f3a"}}
{"seq":2,"ts":"2026-10-12T18:33:41Z","kind":"tool","role":"atlas-dev","request":{"name":"edit","args":{"file":"src/api.ts","old":"…","new":"…"}},"response":{"success":true,"linesChanged":3},"responseHash":"c41d…"}
```

Storage: `$ATLAS_DATA_DIR/runs/<run-id>/cassette.jsonl`, alongside `trajectory.jsonl`. Never rewrite existing entries; a corrected run is a new cassette.

## Replay

Replayer serves recorded exchanges by `seq`. Two invariants, both hard requirements:

1. **Network-free.** Replay performs zero outbound network calls. Any exchange not present in the cassette raises `ReplayMissError` and stops. There is no live fallback, ever: a fallback would silently reintroduce the nondeterminism replay exists to eliminate.
2. **No resampling.** Model responses come from the cassette. Sampling parameters are ignored during replay. Given the same cassette and the same agent code, replay reproduces the original trajectory decisions and tool inputs byte-for-byte after noise normalization.

```text
Replaying run-20261012-docs-rebuild from cassette (412 exchanges)
  seq 1-120: model + tool served from cassette
  seq 121: ReplayMissError, kind=retrieval, query="ACP fork levels", no cassette entry
  Replay aborted at seq 121. The agent attempted an exchange the recorder never captured.
  Options:
    1. Re-record the run with recording covering this path
    2. Switch to lite-mode replay (retrieval misses are live-allowed, see below)
```

### Counterfactual branches

A branch run forks the cassette: keep entries 1..N, replace or drop entries after N, then let the run continue live (the tail is appended to a new branch cassette). This is how "what if the model had answered differently at seq 42" becomes a concrete experiment instead of a re-roll.

## Noise-aware diff

Comparing two cassettes (or a cassette against a re-record) classifies fields before diffing:

| Class | Fields | Default treatment |
|-------|--------|-------------------|
| Noise | `ts`, `meta.*` (latency, request IDs, headers), token usage counts, wall-clock values inside responses | Normalized away; differences reported as a count, never as divergence |
| Signal | `kind`, `role`, `request`, `response` payload bodies, `responseHash`, `seq` ordering | Any difference is a real divergence and fails the comparison |

Diff report shape:

```text
cassette diff: run-a vs run-b
  noise: 37 fields normalized (timestamps, request IDs, latency)
  signal: 1 divergence
    seq 88 kind=model
      response.content differs: "use sed" != "use dos2unix"
```

Purpose: an intermittent "failure" that is pure header or timing noise is not a regression, and a real behavioral change is never buried under timestamp churn.

## Cassette export as regression fixtures

Exported cassettes are the regression inputs for the golden-task eval harness (issue #40):

1. Export strips noise fields (`ts`, `meta`) and keeps signal fields plus `responseHash` per `seq`.
2. Fixture lives with the eval corpus: `eval/fixtures/<task-name>/cassette.fixture.jsonl`.
3. The harness runs each golden task under replay against its fixture. A `ReplayMissError` or a signal-class diff is a regression; noise-class diffs are ignored.
4. Fixtures are frozen once checked in. Re-recording a fixture requires explicit review: silent churn invalidates the regression history the fixture exists to protect.

## Integration

### Trajectory logging (issue #15)

`trajectory.jsonl` stays decision-dense; the cassette stays payload-complete. They link, they do not merge:

- Optional trajectory field `cassetteSeq` points at the exchange entry that produced a decision. Grep trajectory for a `cassetteSeq`, then seek that `seq` in the cassette for the full payload.
- Trajectory never duplicates payloads the cassette already holds; cassette never carries `why` or `outcome` reasoning.
- Live traces and dashboards (observability system) may be derived from cassette entries after the fact, but the cassette is the source of truth for I/O.

### Checkpoint protocol (ACP, issue #6)

- Deep (level 3) checkpoints reference the covering cassette: add `"cassette": {"path": "runs/<run-id>/cassette.jsonl", "lastSeq": 120}` to the checkpoint document.
- ACP Fork Level 1 "Replay" re-runs with live sampling and is therefore best-effort. When a cassette covers the checkpointed range, prefer the deterministic variant: restore the checkpoint, serve every exchange from the cassette up to `lastSeq`, then continue live from there. Without a cassette, say so explicitly instead of implying reproducibility.

### Lite mode

Lite mode (3B-8B models, 8K windows) records and replays model and tool I/O only:

- The lite recorder does not capture `retrieval` or `env` entries at all; `seq` counts only captured kinds, so lite cassettes stay gapless.
- Lite replay treats a `retrieval` or `env` miss as live-allowed and notes it in the replay report. Full-mode replay has no such allowance; lite determinism covers agent logic (model outputs and tool calls), not the full environment.
- Purpose: cheap smoke replay of agent behavior without payload bloat.

## When to record

| Scenario | Record? | Reason |
|----------|---------|--------|
| Intermittent or unreproducible failure | Yes | Only a cassette makes it reproducible |
| Run feeding a golden-task fixture | Yes | Fixture export needs the cassette |
| Routine task with a cheap deterministic re-run | No | Recording cost exceeds re-run cost |
| Run handling secrets that cannot be redacted | No | Cassette would leak or replay would miss |

## Error handling

Corrupt cassette or seq gap:

```text
Error: cassette run-20261012-docs-rebuild.jsonl is not replayable
  seq gap between 57 and 59 (entries are not gapless)
  Re-record the run; a gapped cassette cannot guarantee full coverage.
```

Replay miss (see also the example above): always name the `seq`, `kind`, and request so the gap between recording coverage and replayed behavior is actionable.
