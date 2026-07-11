---
name: frontier-benchmark
category: process
load-when: Self-assessment, comparing against frontier harnesses, monthly review
skip-when: Normal operation
description: Benchmark comparing Atlas capabilities against frontier harnesses (Cursor, Windsurf, Claude Code, etc.).
audience: [atlas-lead, atlas-ent-arch, atlas-ai-eng]
tags: [benchmark, frontier, comparison, capabilities, gaps]
---

# Frontier benchmark

Atlas is benchmarked against frontier harnesses monthly. This file tracks where Atlas leads, is on par, or lags.

## Quick Reference
- Monthly self-assessment triggers benchmark review
- 8 capability categories evaluated
- Gaps drive innovation priorities
- Current version: v0.13.0

## Capability matrix (v0.13.0)

### Where Atlas is AHEAD

| Category | Atlas | Frontier | Delta |
|----------|-------|----------|-------|
| Multi-agent team | 24 specialist roles with full persona, scope, delegation | 0-3 generic agents | Atlas has 8-12x more roles |
| Model-resilient tier cascade | Automatic retry across 3 tiers, never stops | None (quota = failure) | Unique to Atlas |
| Prompt cache optimization | ~800 token stable prefix, 69% reduction | None | Unique to Atlas |
| Workflow state machine | 7-state, conditional injection, small/full variants | Basic state tracking | Atlas has richer state machine |
| Lite mode for small models | ~1,100 token system prompt, 3B-8B support | None (requires large models) | Unique to Atlas |
| Cynefin + structured reasoning | Problem classification, plan-then-action, lookahead | Basic planning | Atlas has deeper reasoning |
| Memory hierarchy | L1/L2/L3 with conflict resolution | Basic memory | Atlas has structured hierarchy |
| Trajectory logging | Full JSONL decision trail with OTel spans | Basic logging | Atlas has richer telemetry |
| ACI enforcement | Structured errors, semantic output, tool provenance, poka-yoke | None | Unique to Atlas |
| Adversarial critics | 5 built-in critics with gapped execution, auto-tuning | Basic code review | Atlas has multi-perspective evaluation |
| DAG orchestration | Dynamic construction, critical path, parallel safety | Basic parallel execution | Atlas has formal DAG |
| Trust scoring (ARTS) | Adaptive role trust with tier allocation | None | Unique to Atlas |
| Knowledge compounding | Retrospective phase, cross-run learning, drift alerts | None | Unique to Atlas |
| Checkpoint protocol | 3-level checkpoints, 3-level fork, cross-surface | Basic session save | Atlas has richer protocol |

### Where Atlas is ON PAR

| Category | Atlas | Frontier | Notes |
|----------|-------|----------|-------|
| Gate/checkpoint system | 3 approval gates, DoD checklists | Similar gate systems | Comparable |
| Universal IDE support | Works on 6+ IDEs | IDE-specific | Atlas is more portable |
| Structured handoffs | 8-section contract with tool provenance | Basic handoffs | Atlas has richer handoffs |
| Context engineering | Progressive disclosure, compaction, sharding | Similar patterns | Comparable |
| Tool usage patterns | Read-before-edit, batch, workdir | Similar patterns | Comparable |

### Where Atlas LAGS (driving future work)

| Category | Atlas | Frontier | Gap |
|----------|-------|----------|-----|
| Runtime execution layer | Prompt-only (no direct execution) | AgentSDK, Bash, tool calls | CRITICAL — no programmatic execution |
| Codebase-aware context | Manual file reading | Semantic search, embeddings, AST | HIGH — manual discovery vs intelligent retrieval |
| Production observability | OTel spans (no dashboard) | Live dashboards, alerting, SLOs | HIGH — no real-time monitoring |
| OS-level sandboxing | None | Docker, gVisor, Firejail | MEDIUM — no isolation for untrusted code |
| Session checkpointing | JSON files (no streaming) | Real-time state sync | MEDIUM — manual vs automatic |

## Monthly review process

1. Atlas-lead reviews this benchmark against current frontier harnesses
2. Identifies new gaps or improvements
3. Proposes innovation priorities for next month
4. User approves priorities
5. Updates this file with new findings

## Anti-patterns

- Benchmarking against outdated harness versions
- Ignoring gaps because "Atlas is good enough"
- Adding features just to match frontier without user need
- Not updating this benchmark when frontier harnesses release new features
