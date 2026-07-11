---
name: structured-reasoning
category: process
load-when: Complex multi-step tasks, architectural decisions, debugging
skip-when: Simple single-step tasks, formatting, renaming
description: Dense, logical reasoning patterns for complex tasks.
audience: [all]
tags: [reasoning, planning, decision-making]
---

# Structured reasoning

Reasoning should be dense, logical, and purposeful, not narrative.

## Quick Reference
- Plan-then-action: 2-5 step plan before detailed work
- Thought-Action-Observation: observe, decide, execute, observe result
- Atomic reasoning: one logical primitive per step
- Lookahead: consider 2-3 paths before committing

## Patterns

- **Plan-then-action:** before complex tasks (multi-step implementation, cross-role coordination), generate a 2-5 step plan before detailed reasoning. The plan is a scaffold that keeps reasoning focused.
- **Thought-Action-Observation loop:** for each step, state what you observe, decide what action to take, execute, and observe the result. Don't skip steps or act without reasoning.
- **Atomic reasoning:** keep reasoning dense and logical. Each reasoning step should be a single logical primitive, not a paragraph of narration.
- **Lookahead simulation:** at decision points, briefly consider 2-3 possible next steps and their likely outcomes before committing. Choose the path with highest expected value.

## When to use which

| Pattern | Use when | Skip when |
|---------|----------|-----------|
| Plan-then-action | 3+ steps, cross-role, unfamiliar codebase | Single-step, clear path |
| TAO loop | Debugging, iterative refinement | Obvious solution |
| Atomic reasoning | Complex trade-offs, architecture | Simple decisions |
| Lookahead | Irreversible decisions, branching paths | Reversible actions |
