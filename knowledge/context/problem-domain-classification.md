---
name: problem-domain-classification
category: process
load-when: Starting any task, unsure how to approach a problem
skip-when: Clear continuation of known work, single-step actions
description: Cynefin domain classification. Diagnose the nature of a problem before choosing strategy.
audience: [all]
tags: [cynefin, classification, strategy, decision-making]
---

# Problem domain classification (Cynefin)

Before choosing a strategy, classify the task. Wrong strategy for the wrong domain is the most common agent failure.

## Quick Reference
- **Clear:** known solution. Execute directly. Checklists, no planning.
- **Complicated:** discoverable through analysis. Plan, consult, analyze.
- **Complex:** understood in retrospect. Probe, experiment, adapt.
- **Chaotic:** no cause-effect. Act immediately to stabilize.

## Domains

### Clear (obvious, known solution)
Execute directly. Checklists, automation, no planning needed.
Examples: format a file, run a linter, rename a variable, apply a known fix.

### Complicated (discoverable through analysis)
Plan, consult expertise, analyze before acting. The right approach exists but requires investigation.
Examples: refactor a module, optimize a query, design an API, integrate a library.

### Complex (only understood in retrospect)
Probe with experiments. Try small actions, observe results, adapt. Do not attempt to plan the full path.
Examples: design a new feature, navigate an unfamiliar codebase, integrate with an unknown system, debug a race condition.

### Chaotic (no cause-effect relationship)
Act immediately to stabilize. Stop the bleeding, then analyze.
Examples: production down, data corruption, unknown system state, security breach.

## Strategy mapping

| Domain | Strategy | Agent behavior |
|--------|----------|----------------|
| Clear | Sense-Categorize-Respond | Execute checklist, no reasoning needed |
| Complicated | Sense-Analyze-Respond | Plan, research, then execute |
| Complex | Probe-Sense-Respond | Experiment, observe, adapt iteratively |
| Chaotic | Act-Sense-Respond | Stabilize first, analyze after |

## Domain shifts
If the domain shifts mid-task (clear becomes complex when context changes), re-evaluate your strategy. Don't keep executing a checklist when the problem has become complex.
