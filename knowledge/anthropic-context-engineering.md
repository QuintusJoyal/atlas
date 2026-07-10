---
name: anthropic-context-engineering
load-when: Managing context windows, optimizing token usage, designing agent prompts
skip-when: Specific AI risks (see owasp-llm-top-10), model documentation (see model-cards)
---

# Context Engineering

## Quick Reference
- Context is the most valuable resource in LLM applications
- Progressive disclosure: load only what's needed, when needed
- Just-in-time loading: defer loading until the current step requires it
- Tool-as-context: extract relevant findings, not raw output
- Structured note-taking: persist notes for long tasks
- Compaction: summarize when context exceeds ~80% of window

## Deep Dive

### Progressive Disclosure
- Start with summaries or section references
- Load full content only when the current step needs it
- Use paths and pointers, not dumps
- Design documents with clear H2/H3 sections for selective loading

### Just-in-Time Loading
- Load knowledge only when the current step needs it
- Use search (grep) instead of loading full files
- Playbook contains the search index for role-specific knowledge

### Tool-as-Context
After a tool call:
- Extract only relevant findings
- Don't carry raw output forward
- Keep paths, line references, and key findings
- Discard the rest

### Structured Note-Taking
On long tasks:
- Persist notes to a file
- Reference notes instead of re-deriving context
- Include current state, owned artifacts, delegation state

### Compaction
When to compact:
- Sub-task is resolved
- Context exceeds ~80% of model window
- Switching phases

When NOT to compact:
- Mid-derivation
- During active reasoning chains
- When working on multiple parallel tasks

### Token Budget Guidelines
- Routine task: 2-3 quick refs (~400-600 tokens)
- Complex task: 3-5 quick refs + 1 deep dive (~1,500-2,500 tokens)
- Hard cap: 5,000 tokens of knowledge loading per task

## See Also
- **model-resilience.md** — Model failure handling and compaction
- **atlas-core.md** — Core rules including context engineering
- **model-cards** — Model documentation
- **nist-ai-rmf** — AI risk management
