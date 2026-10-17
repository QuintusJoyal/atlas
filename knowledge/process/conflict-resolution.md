---
name: conflict-resolution
category: process
load-when: Two or more agents produce competing outputs for the same task, or a critic contradicts an author
skip-when: Single-agent tasks, no shared artifact
description: Detect contradictions between agent outputs with configurable similarity thresholds, resolve them by consensus vote, priority-weighted selection, or human escalation, and log a structured disagreement manifest.
audience: [atlas-lead, atlas-ent-arch]
tags: [conflict, cross-validation, consensus, arbitration, multi-agent, disagreement-manifest]
---

# Conflict resolution and cross-validation

`divergence-detection.md` catches conflicts between parallel artifacts at a stage boundary. `adversarial-critics.md` produces structured verdicts. This protocol unifies both: cross-validation (one agent reviews another's output), semantic comparison with configurable thresholds, and a deterministic resolution path when positions cannot be reconciled.

## Quick Reference
- Run when two agents produce competing outputs for the same task, or a critic verdict contradicts the author
- Detect by semantic diff, not exact string match — configurable threshold per artifact type
- Resolve in order: consensus vote → priority-weighted selection → human escalation
- Always emit a disagreement manifest; always log the outcome to trajectory.jsonl
- Cross-validation reviewer must be a different role than the producer (same isolation rule as critics)

## Conflict detection (semantic comparison)

For each pair of competing outputs, compare on four axes. This extends the divergence checks with a similarity score so near-agreements are not escalated.

| Axis | What is compared | Example conflict |
|------|------------------|------------------|
| Terminology | Noun phrases / concept names | "export pipeline" vs "data flow" |
| Assumptions | Technology and policy choices | REST vs GraphQL, Postgres vs Mongo |
| Interfaces | Contracts, schemas, signatures | `userId: string` vs `userId: number` |
| Claims | Factual or requirement statements | "endpoint requires auth" vs "endpoint is public" |

Score each axis with a similarity threshold. Thresholds are per artifact type, because code and prose diverge differently:

| Artifact type | Default threshold | Rationale |
|---------------|-------------------|-----------|
| Interface / API contract | 0.95 | Any contract drift is a defect; compare structures, not prose |
| Data model / schema | 0.90 | Field names and types must align |
| Design / architecture prose | 0.75 | Paraphrase is acceptable; concepts must match |
| Free-form explanation | 0.60 | Wording varies widely; only flag genuine contradictions |

- **Similarity ≥ threshold:** treat as agreement; merge the artifacts.
- **Similarity < threshold:** a conflict exists; build the disagreement manifest.
- Thresholds are advisory defaults. A role may override with a stated reason (record it in the manifest under `thresholdOverride`).

Semantic comparison is a reasoning step performed by atlas-lead (2-5 turns), not a separate delegation. Compare structured extracts (contracts, schemas, file paths), not raw token strings.

## Structured disagreement manifest

Emitted whenever similarity falls below threshold. One manifest per conflict, appended to the audit log. It records what differs, why, and which agents hold each position.

```json
{
  "conflictId": "conflict-2026-10-17-001",
  "task": "design-stage: export feature",
  "axis": "interface",
  "similarity": 0.42,
  "threshold": 0.95,
  "positions": [
    {
      "agent": "atlas-architect",
      "claim": "POST /exports returns 202 with jobId",
      "artifact": "docs/design/export-api.md:12",
      "priority": 70
    },
    {
      "agent": "atlas-dev",
      "claim": "POST /exports returns 200 with the file body",
      "artifact": "src/exports/router.ts:31",
      "priority": 50
    }
  ],
  "why": "Sync vs async export contract; architect and dev implemented different response shapes",
  "resolution": null
}
```

- `axis` and `similarity` come from detection.
- `positions[].priority` is the agent's effective priority for this task (role priority from `team-charter.md`, adjusted by ownership: the role that owns the artifact soars).
- `resolution` is filled in by the resolution step below; a null resolution means unresolved.

## Resolution strategies

Apply in order. Stop at the first strategy that produces a decision.

### 1. Consensus vote (≥N/2 agree)
**When:** three or more agents produced output, or a panel reviewed the competing positions.
**Rule:** a position wins if strictly more than half of the participating agents endorse it (≥ N/2 of N participants). With two agents this cannot produce a majority — skip to strategy 2.
**Record:** `resolution: {strategy: "consensus", winner: "<agent>", votes: {"<agent>": "<position-agent>"}}`.

### 2. Priority-weighted selection
**When:** consensus has no majority, or exactly two agents conflict.
**Rule:** the position held by the agent with the highest effective priority wins. Ties break by ownership (the role that owns the artifact), then by evidence quality (citations beat assertions), then by simplicity — matching `team-charter.md`'s arbitration order (simplicity, evidence, security first).
**Record:** `resolution: {strategy: "priority", winner: "<agent>", priorities: {...}, tieBreak: "<rule>"}`.

### 3. Escalate to human
**When:** priorities tie and no tie-break applies, the conflict touches a security or compliance boundary, or an agent explicitly refuses the outcome.
**Rule:** pause, present both positions with a recommendation using the T3 payload in `escalation-tiers.md`. Do not merge competing artifacts silently.
**Record:** `resolution: {strategy: "escalation", recommendation: "<agent>", options: ["A", "B"]}`.

## Cross-validation

Cross-validation is the input that makes conflict detection trustworthy: before comparing two outputs, have one agent review the other's. The reviewer must differ from the producer (same isolation rule as `adversarial-critics.md`). The reviewer returns the same structured critic shape so its verdict can itself become a `position` in the manifest:

```json
{
  "critic": "cross-validation",
  "target": "docs/design/export-api.md",
  "producer": "atlas-architect",
  "reviewer": "atlas-dev",
  "verdict": "fail",
  "findings": [
    {"category": "interface-mismatch", "severity": "high", "detail": "response shape contradicts src/exports/router.ts"}
  ],
  "evidence": "docs/design/export-api.md:12",
  "confidence": 0.8
}
```

For orchestrator-worker topologies, atlas-lead cross-validates worker outputs against each other. For peer-to-peer topologies, peers cross-validate directly and escalate only unresolved conflicts to atlas-lead.

## Integration with A2A (#13)

Conflict signaling reuses the A2A agent-to-agent envelope once it lands. Until then, signal conflicts in-band via the handoff artifact and `conflictId`.

When A2A is available, wrap the manifest in a conflict signal:

```json
{
  "type": "conflict",
  "conflictId": "conflict-2026-10-17-001",
  "from": "atlas-dev",
  "to": ["atlas-architect", "atlas-lead"],
  "manifestRef": "conflict-2026-10-17-001",
  "requires": "resolution"
}
```

- `to` always includes every agent holding a position plus atlas-lead (the arbiter).
- A2A transports the signal; it does not decide the conflict — resolution stays with this protocol.
- If A2A is unavailable, the same fields are attached to the handoff artifact and relayed by atlas-lead.

## Audit log

Every conflict and its resolution is one plain JSONL entry in `trajectory.jsonl`, per `knowledge/process/trajectory-logging.md` — no fabricated tracing spans.

Conflict logged:
```json
{"ts": "2026-10-17T14:30:00Z", "role": "atlas-lead", "action": "conflict-detect", "target": "design-stage", "outcome": "divergence-detected", "why": "interface similarity 0.42 < 0.95", "conflictId": "conflict-2026-10-17-001"}
```

Resolution logged:
```json
{"ts": "2026-10-17T14:32:00Z", "role": "atlas-lead", "action": "conflict-resolve", "target": "conflict-2026-10-17-001", "outcome": "success", "why": "priority-weighted: atlas-architect (70 > 50)"}
```

Both entries reference the `conflictId` so post-run analysis can join detection to resolution. The full manifest is retained alongside the run so a reviewer can reconstruct positions, not just the outcome.

## Integration with existing protocols

- `divergence-detection.md` runs at the parallel-stage boundary; when it finds a conflict, hand off to this protocol for cross-validation and resolution.
- `adversarial-critics.md` verdicts feed in as `positions`; a `fail` verdict that contradicts the author opens a conflict.
- `team-charter.md` supplies priority and the arbitration order; `escalation-tiers.md` supplies the human-escalation payload.
- `handoff-protocol.md` carries the conflict signal in-band when A2A is unavailable.

## Anti-patterns

- Exact string matching when comparing prose — flag noun-phrase and interface diffs, then score semantically
- One similarity threshold for all artifacts (contracts and prose diverge at different rates)
- Letting the producer cross-validate its own output
- Merging competing artifacts silently to "keep moving"
- Resolving without writing the manifest — the audit trail is the point
- Escalating every low-similarity pair to a human before trying consensus or priority
