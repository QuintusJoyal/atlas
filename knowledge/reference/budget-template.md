---
name: budget-template
category: template
description: Token budget template for kickoff — predicted usage, role estimates, and downgrade tracking.
audience: [atlas-lead, atlas-ai-eng]
tags: [budget, token-usage, template, kickoff]
---

# Token budget

Run: <run-id>
Workflow: <feature|bugfix|data-project|infra-change|security-audit|discovery>
Workflow rationale: <one line why this preset>

Predicted: pending
Approved by user: pending

## Estimates by role
<!-- Each participating role: - atlas-<role>: light|medium|heavy (one-line rationale) -->
<!-- Populated by estimation huddle (atlas-ai-eng aggregates). Lead does not guess. -->
<!-- Optional: include compute-profile/target tier: e.g., target: premium|standard|fast|auto (aliases: frontier/mid/small) -->

## Compute profile
<!-- Declarative compute profile per agent role (runtime gateway) -->
<!-- Format: atlas-<role>: frontier|mid|small|auto (resolved via manifest.tiers) -->
<!-- Example: atlas-lead: mid (standard); atlas-dev: small (fast); atlas-qa: mid; atlas-architect: frontier (premium) -->

## Actual
<!-- Filled at final delivery or post-run -->
<!-- Include cost per role if available: e.g., - atlas-dev: tokens 12000, est_cost_usd 0.004, tier fast -->

## Cost telemetry
<!-- Per-role cost tracking (self-reported in v1; directional) -->
<!-- Format: - role: atlas-dev | tier: fast | tokens: <n> | est_cost_usd: <x> | budget_usd: <y> | over_budget: true|false | notes: ... -->
<!-- Roll up totals and % vs all-frontier baseline if computed -->

## Downgrades
<!-- One line per downgrade per model-resilience.md -->
