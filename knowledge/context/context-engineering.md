---
name: context-engineering
category: process
load-when: Starting a complex task, context feels bloated, switching phases
skip-when: Simple single-step tasks, short conversations
description: Treat context as a finite, high-value resource. Every token must earn its place.
audience: [all]
tags: [context, tokens, loading, efficiency]
---

# Context engineering

Treat context as a finite, high-value resource. Every token must earn its place.

## Quick Reference
- Progressive disclosure: summaries first, full content on demand
- Just-in-time loading: load only what the current step needs
- Position-aware ordering: critical content at top and bottom, supporting data in middle
- Tool-as-context: extract findings, discard raw output
- Structured note-taking: persist to notes.md, reference instead of re-deriving
- Compaction triggers: after sub-task, at 80% context, on phase switch

## Principles

- **Progressive disclosure:** don't load everything up front. Start with summaries or section references. Load full content only when the current step needs it. Use paths and pointers, not dumps.
- **Just-in-time loading:** load knowledge and playbook content only when the current step needs it. The three-tier loading strategy in atlas-core.md is the primary mechanism.
- **Tool-as-context:** after a tool call, extract only the relevant findings. Don't carry raw output (full file contents, detailed logs) forward into the next step. Keep paths, line references, and key findings.
- **Structured note-taking:** on long tasks, persist notes to `$ATLAS_DATA_DIR/runs/<run-id>/notes.md`. Reference notes instead of re-deriving context from earlier turns.
- **Compaction triggers:** compact when (a) a sub-task is resolved, (b) context exceeds ~80% of the model window, (c) switching phases. Don't compact mid-derivation or during active reasoning chains. See `knowledge/reference/model-resilience.md` for the full rubric.

## Position-aware ordering (lost-in-the-middle mitigation)

LLM attention is U-shaped: content at the beginning and end of context is recalled well, content in the middle is forgotten (30-40% accuracy loss mid-context, even at 4K tokens). Order context by attention value, not by load order. This changes HOW context is arranged, not WHAT is loaded — the three-tier loading strategy and its budget are unchanged.

**Layout template:**

```
[STATIC_TOP]       role rules, non-negotiables, stable instructions (byte-stable)
[RETRIEVED_EVIDENCE]  grepped lessons, loaded knowledge files, tool findings
[IMMEDIATE_TASK]   the current question, acceptance criteria, next action
```

**Rules:**
- Keep critical instructions in `STATIC_TOP` (atlas-core, playbook rules) — loaded first, never displaced by retrieval.
- Place retrieved evidence (tier 2/3 knowledge loads, grep hits) in the middle. Middle placement is acceptable for supporting data; keep each load scoped so it can't push the task out.
- Put the immediate task or question at the bottom — last position is the other high-attention zone.
- Use structured formatting (headers, numbered sections, tables) for anything in the middle; structured layout improves retrieval from mid-context.
- When context grows, compact or summarize the middle first — never trim `STATIC_TOP` or `IMMEDIATE_TASK`.

See `knowledge/context/prompt-cache-strategy.md` for how this interacts with cache breakpoints.

## Anti-patterns
- Loading a full knowledge file when a grep would suffice
- Carrying raw tool output into the next reasoning step
- Re-reading files you already summarized
- Asking the user for information you can find in the codebase
- Appending retrieved knowledge after the current task, pushing the task into the middle
