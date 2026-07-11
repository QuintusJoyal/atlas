---
name: prompt-cache-strategy
category: process
load-when: Designing system prompts, optimizing token costs, IDE configuration
skip-when: Normal operation, simple tasks
description: Cache-optimized prompt ordering. Static content first, dynamic content last.
audience: [atlas-lead, atlas-ent-arch]
tags: [caching, tokens, prompt-optimization, cost]
---

# Prompt cache strategy

Most IDEs don't give direct control over caching, but you can structure content to maximize cache hits.

## Quick Reference
- Static rules first, dynamic context last
- Stable prefix = cache hit on subsequent turns
- `cache_control` breakpoint concept for Anthropic/OpenAI
- Progressive loading defeats caching if not ordered carefully

## The problem

Atlas uses progressive loading: load only what the current step needs. But loading different content each turn defeats prefix caching — the system prompt changes every turn, so nothing is cached.

The solution: order content so the **stable prefix** (always-loaded rules) comes first, and **variable content** (task-specific knowledge) comes last.

## Ordering principle

```
[STATIC — cached across turns]
  1. atlas-core.md (non-negotiables)
  2. Bootstrap steps
  3. Load-on-demand list
[DYNAMIC — changes per turn]
  4. Task-specific knowledge (loaded via grep/load)
  5. Workflow state
  6. Tool output
```

Items 1-3 are identical every turn. Items 4-6 change. If the IDE caches the system prompt, items 1-3 are cached; only 4-6 are re-processed.

## Cache control breakpoint

Some APIs support explicit cache control:

**Anthropic:** `cache_control: {type: "ephemeral"}` on a message block. 5-minute TTL. 90% discount on cached prefix tokens.

**OpenAI:** `prompt_cache` field. Automatic prefix caching. Similar discount.

For Atlas: the optimal breakpoint is after the always-loaded rules and before the first on-demand load. IDEs that support cache control should place the breakpoint between static and dynamic content.

## Atlas-specific guidance

### atlas-core.md ordering
The slimmed atlas-core (v0.12.0) is structured for cache optimization:
1. Non-negotiables (always static)
2. Bootstrap (always static)
3. Knowledge loading list (always static)
4. Pointers to on-demand knowledge (static, but the loaded content varies)

The pointers are static text. The knowledge they point to is dynamic. This means the system prompt prefix is stable.

### On-demand loading
When loading knowledge files, load them as context (not system prompt) when possible. System prompt changes defeat caching. Context changes don't affect the system prompt cache.

### Lite mode
Lite mode is already cache-optimized: ~1,100 token system prompt that's identical every turn. The small set of always-loaded rules creates a tight, stable prefix.

## Anti-patterns
- Loading different knowledge files as system prompt each turn (defeats cache)
- Placing dynamic content (task state, tool output) before static rules
- Changing atlas-core.md content mid-session (invalidates cache)
