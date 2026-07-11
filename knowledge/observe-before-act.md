---
name: observe-before-act
category: process
load-when: Before any code change or significant action
skip-when: Formatting, renaming, known-safe operations
description: Gemba principle. Read, test, understand before modifying. Prevents acting on assumptions.
audience: [all]
tags: [gemba, observation, understanding, prevention]
---

# Observe before act (Gemba)

Before any code change or significant action:

## Quick Reference
1. Read relevant files (don't assume contents)
2. Run relevant tests (don't assume they pass)
3. Check git log for recent changes to the area
4. Understand WHY existing code is structured as it is

## The rule

Do not fix on the spot. Observe, document, then plan the intervention. Agents that immediately start modifying code without understanding the full picture create as many problems as they solve.

## Observation checklist

1. **Read the relevant files.** Don't assume what's in them. Read them.
2. **Run the relevant tests.** Don't assume they pass. Run them.
3. **Check git log.** Recent changes to the area may explain current structure.
4. **Understand WHY.** Existing code is structured as it is for a reason. Find the reason before changing it.

## When to skip
- Formatting changes (whitespace, indentation)
- Renaming variables/functions with clear scope
- Applying known-safe patches from authoritative sources
- Simple typo fixes
