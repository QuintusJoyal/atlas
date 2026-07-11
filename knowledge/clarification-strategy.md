---
name: clarification-strategy
category: process
load-when: Ambiguous requirements, unclear specifications, user asks open-ended question
skip-when: Clear specs, known solution, single valid approach
description: Know when to ask the user and when to proceed. Reduce unnecessary questions.
audience: [all]
tags: [clarification, questions, requirements, ambiguity]
---

# Clarification strategy

Not every ambiguity requires a question. Know when to ask and when to proceed.

## Quick Reference
- Ask when: spec uncertainty high, action confidence low, critical info missing
- Proceed when: spec clear enough, action reversible, info findable
- State what you know, what's unclear, what you need
- Batch questions into one ask, don't pepper

## When to ask

- Specification uncertainty is high (ambiguous requirements, missing constraints)
- Action confidence is low (multiple valid approaches with different trade-offs)
- Critical information is missing with no source to find it

## When to proceed

- Spec is clear enough to act (even if not perfect)
- The action is reversible
- The information can be found (codebase, docs, MCP)

## How to ask

- State what you know, what is unclear, and what specific information you need.
- Offer options when possible. Don't ask open-ended questions.
- **Information gain:** only ask when the question will materially change the outcome. Don't ask for the sake of asking.
- **Consolidation:** when multiple questions arise, batch them into a single ask rather than peppering the user individually.
