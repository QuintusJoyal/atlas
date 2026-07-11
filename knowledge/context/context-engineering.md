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
- Tool-as-context: extract findings, discard raw output
- Structured note-taking: persist to notes.md, reference instead of re-deriving
- Compaction triggers: after sub-task, at 80% context, on phase switch

## Principles

- **Progressive disclosure:** don't load everything up front. Start with summaries or section references. Load full content only when the current step needs it. Use paths and pointers, not dumps.
- **Just-in-time loading:** load knowledge and playbook content only when the current step needs it. The three-tier loading strategy in atlas-core.md is the primary mechanism.
- **Tool-as-context:** after a tool call, extract only the relevant findings. Don't carry raw output (full file contents, detailed logs) forward into the next step. Keep paths, line references, and key findings.
- **Structured note-taking:** on long tasks, persist notes to `$ATLAS_DATA_DIR/runs/<run-id>/notes.md`. Reference notes instead of re-deriving context from earlier turns.
- **Compaction triggers:** compact when (a) a sub-task is resolved, (b) context exceeds ~80% of the model window, (c) switching phases. Don't compact mid-derivation or during active reasoning chains. See `knowledge/reference/model-resilience.md` for the full rubric.

## Anti-patterns
- Loading a full knowledge file when a grep would suffice
- Carrying raw tool output into the next reasoning step
- Re-reading files you already summarized
- Asking the user for information you can find in the codebase
