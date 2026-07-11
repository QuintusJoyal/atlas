---
name: performance-benchmarks
category: process
load-when: Optimizing token usage, comparing Atlas modes, measuring efficiency
skip-when: Normal operation
description: Performance benchmarks for Atlas. Token usage measurements across workflows, roles, and modes.
audience: [atlas-lead, atlas-ai-eng]
tags: [performance, benchmarks, tokens, efficiency, measurements]
---

# Performance benchmarks

Atlas performance is measured across workflows, roles, and modes. These benchmarks help optimize token usage and compare Atlas against raw prompting.

## Quick Reference
- System prompt: ~800 tokens (full), ~1,100 tokens (lite)
- Knowledge loading: ~400-600 tokens (routine), ~1,500-2,500 tokens (complex)
- Delegation overhead: ~500 tokens per delegation
- Cache hit rate: ~80% for stable prefix

## Token usage by workflow variant

### Feature workflow

| Phase | Small (tokens) | Full (tokens) | Notes |
|-------|---------------|---------------|-------|
| Kickoff | 0 | 200 | Estimation huddle (full only) |
| Requirements | skipped | 1,200 | atlas-pm + atlas-ba |
| Design | skipped | 3,500 | atlas-architect + atlas-ux |
| Implementation | 1,400 | 1,400 | atlas-dev |
| Testing | 800 | 800 | atlas-qa |
| Review | skipped | 1,200 | atlas-reviewer + atlas-security |
| Deploy | 400 | 400 | atlas-devops |
| Retrospective | 200 | 200 | atlas-lead |
| **Total** | **2,800** | **8,900** | |

### Bugfix workflow

| Phase | Small (tokens) | Full (tokens) | Notes |
|-------|---------------|---------------|-------|
| Triage | 400 | 600 | atlas-maintenance |
| Fix | 1,000 | 1,000 | atlas-dev |
| Test | 600 | 600 | atlas-qa |
| Review | 400 | 800 | atlas-reviewer |
| Deploy | 400 | 400 | atlas-devops |
| Retrospective | 200 | 200 | atlas-lead |
| **Total** | **3,000** | **3,600** | |

## Token usage by role

| Role | Light (tokens) | Medium (tokens) | Heavy (tokens) |
|------|---------------|-----------------|----------------|
| atlas-lead | 500 | 1,000 | 2,000 |
| atlas-dev | 1,000 | 3,000 | 6,000 |
| atlas-qa | 600 | 1,500 | 3,000 |
| atlas-architect | 800 | 2,000 | 4,000 |
| atlas-pm | 400 | 1,000 | 2,000 |
| atlas-security | 600 | 1,500 | 3,000 |
| atlas-devops | 400 | 800 | 1,500 |

## Knowledge loading overhead

| Strategy | Tokens | When to use |
|----------|--------|-------------|
| Inline (playbook) | ~200 | Routine tasks |
| Grep (search) | ~400 | Need specific info |
| Full file load | ~1,500 | Complex/unusual tasks |
| **Budget cap** | **5,000** | **Maximum per task** |

## Prompt cache effectiveness

| Component | Tokens | Cached? |
|-----------|--------|---------|
| atlas-core.md | ~800 | Yes (stable prefix) |
| Role playbook | ~180 | Yes (stable prefix) |
| Knowledge search | ~400 | No (dynamic) |
| Task context | ~1,000 | No (dynamic) |
| **Total** | **~2,380** | **~980 cached (41%)** |

Cache hit rate: ~80% for repeated sessions with same role.

## Comparison: Atlas vs Raw Prompting

| Metric | Atlas Full | Atlas Lite | Raw Prompting |
|--------|-----------|------------|---------------|
| System prompt | ~800 tokens | ~1,100 tokens | ~200 tokens |
| Knowledge loading (routine) | ~400-600 | ~200-300 | 0 |
| Knowledge loading (complex) | ~1,500-2,500 | ~500-800 | 0 |
| Delegation overhead | ~500 | ~200 | 0 |
| Quality (composite score) | 0.91 | 0.82 | 0.75 |
| Time to complete (feature) | 15-20 min | 10-15 min | 5-10 min |
| Token cost (feature) | ~9,000 | ~5,000 | ~3,000 |

### Analysis

**Atlas Full** costs ~3x raw prompting in tokens but delivers:
- Higher quality (0.91 vs 0.75 composite score)
- Structured handoffs (no context loss)
- Model resilience (never stops on failure)
- Audit trail (trajectory logging)
- Multi-agent coordination (24 roles)

**Atlas Lite** costs ~1.7x raw prompting and delivers:
- Better quality than raw (0.82 vs 0.75)
- Structured handoffs
- Model resilience
- Works on 3B-8B models

## Optimization targets

| Metric | Current | Target | Strategy |
|--------|---------|--------|----------|
| System prompt | ~800 tokens | ~600 tokens | Further extraction |
| Knowledge loading | ~400-600 | ~200-300 | Better caching |
| Delegation overhead | ~500 tokens | ~300 tokens | Compressed briefs |
| Cache hit rate | ~80% | ~90% | More stable prefix |

## Measurement methodology

Benchmarks are measured by:
1. Running each workflow variant 10 times
2. Recording token usage per phase via OTel spans
3. Calculating averages and percentiles
4. Comparing against baseline (raw prompting)

**Note:** These are estimates based on typical usage. Actual token usage varies by task complexity, codebase size, and model.
