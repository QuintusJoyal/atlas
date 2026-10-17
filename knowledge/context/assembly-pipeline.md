---
name: assembly-pipeline
category: process
load-when: Assembling context for a multi-source turn, context overflow, conflicting or redundant sources in window
skip-when: Single-source turns, short conversations
description: Governed context assembly. Compose the window from named slots with priority, compression, and budget per slot.
audience: [all]
tags: [context, assembly, slots, budget, dedup, telemetry]
---

# Context assembly pipeline

Compose each turn's context deliberately from named slots instead of stuffing sources in as they arrive. Every slot has a fixed position, a token budget, a compression mode, and an eviction rank. Assemble in priority order, compress to budget, deduplicate, then send.

## Quick Reference
- 6 slots: system, memory, steps, rag, tools, task
- Assembly order: `[STATIC_TOP] [RETRIEVED_EVIDENCE] [IMMEDIATE_TASK]` (see `context-engineering.md`)
- Eviction order (first out): tools > rag > steps > memory > task > system
- Compression: system/task/memory = full; steps = summary; rag = extractive; tools = extractive
- Hard cap: 5,000 tokens of loaded knowledge per task (atlas-core budget)
- One telemetry line per assembly in the trajectory log

## Slots

| Slot | Contents | Position | Budget | Compression | Eviction rank |
|------|----------|----------|--------|-------------|---------------|
| system | always-on rules, role, non-negotiables | STATIC_TOP | fixed, never trimmed | full | 6 (last out) |
| memory | lessons, notes, project knowledge | STATIC_TOP | ≤15% | full | 5 |
| steps | prior execution steps, checkpoints | RETRIEVED | ≤20% | summary | 3 |
| rag | retrieved documents, grep hits, loaded knowledge | RETRIEVED | ≤30% | extractive | 2 |
| tools | tool results, file reads, search output | RETRIEVED | ≤20% | extractive | 1 (first out) |
| task | current question, acceptance criteria, next action | IMMEDIATE_TASK | fixed, never trimmed | full | 4 |

Budgets are shares of the turn's context allowance, not absolute sizes. The task and system slots are reserved: their size is whatever they need; the remaining slots share what is left and shrink per the eviction order when the total exceeds the budget.

## Assembly steps

1. **Collect.** Gather candidate content per slot. Nothing enters the window unslotted.
2. **Compress.** Apply the slot's mode: `full` (verbatim), `summary` (one-line-per-item state block), `extractive` (keep decisive lines, paths, line numbers, drop raw output). Tools are always extractive — findings in, raw logs out. See `context-engineering.md` "Tool-as-context".
3. **Deduplicate.** Before inserting, drop content a higher-priority slot already covers (rules below).
4. **Order.** Place slots per the layout template. Position never changes what was loaded, only where it sits.
5. **Log.** Append one telemetry line (below) to the trajectory log.

## Deduplication

Redundant or contradictory content across slots is the main assembly failure mode. Rules, highest wins:

1. **Same fact in two slots:** keep the higher-ranked slot's copy, drop the other. A lesson in `memory` beats the same finding re-derived in `tools`.
2. **Same file twice:** never carry a summary and the full version. Keep one, per progressive disclosure.
3. **Conflicting claims:** apply the memory hierarchy — L1 personal > L2 project > L3 shared, explicit decisions > patterns (`memory-hierarchy.md`). Note the losing claim as superseded, don't argue both.
4. **Stale steps:** a step superseded by a later step or checkpoint is dropped, not summarized twice.

## Telemetry

One JSONL line per assembly, appended to the trajectory log (`knowledge/process/trajectory-logging.md`):

```
{"event":"context_assembly","slots":{"system":820,"memory":310,"steps":450,"rag":980,"tools":640,"task":210},"total":3410,"budget":5000,"evicted":["tools:raw-log-3"],"overflow":false}
```

- **tokens per slot:** estimated, post-compression.
- **evictions:** one entry per dropped block, slot-prefixed. An empty list is the healthy case.
- **overflow:** `true` when even after eviction the total exceeds budget — the turn must pause and re-approve per the token-budget rule in atlas-core, or compact and continue per the compaction trigger.

## Integration

- **Ordering (#3):** this pipeline decides WHAT enters the window and HOW MUCH; `context-engineering.md` decides WHERE it sits. Assembly output is always laid out as `[STATIC_TOP] [RETRIEVED_EVIDENCE] [IMMEDIATE_TASK]`.
- **Compaction (#24):** the 80% compaction trigger runs the pipeline again over the compacted state — prior turns collapse into the `steps` slot as a summary block, then slots are re-filled and re-deduplicated. Never compact `system` or `task`.
- **Checkpointing:** a restored checkpoint re-enters as the `steps` slot, summary mode, not as raw history.

## Anti-patterns
- Ad-hoc stuffing: appending a tool dump or RAG result with no slot, budget, or compression
- Compressing `system` or `task` to make room — evict `tools` first instead
- Keeping two copies of the same finding because they arrived from different sources
- Skipping the telemetry line: an assembly with no cost record can't be tuned
