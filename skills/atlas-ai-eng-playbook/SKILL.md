---
name: atlas-ai-eng-playbook
description: AI engineering and team-optimization methodology for atlas-ai-eng: RAG, agents, eval, guardrails, and efficiency analysis. Use when atlas-ai-eng runs.
disable-model-invocation: true
---

# AI and LLM engineer playbook

Standards: RAG and evaluation best practices, agent design, guardrails, responsible AI (NIST AI RMF).

## RAG and agents
Ground answers in retrieved context. Chunk and index deliberately. For agents, define tools, stop conditions, and failure handling.

## Evaluation
Build an eval set before claiming quality. Measure accuracy, grounding, and regressions. No unverified quality claims.

## Guardrails and responsible AI
Input and output validation, prompt-injection defenses, PII handling, and human oversight for high-impact actions.

## Team optimization (dual mandate)
Track usage patterns in `~/.cursor/atlas-knowledge/usage-insights.md`:
- Bottleneck roles, recurring rework or loops, repeated questions.
- Premium-tier overuse and slow handoffs.
Aggregate work-size estimates into light, medium, or heavy for the token-budget protocol. Raise prioritized efficiency suggestions through the ways-of-working queue. Prune stale lessons (proposed for approval). Never store secrets or PII.

## Estimation huddle (atlas-lead kickoff)
When Task-delegated for kickoff, return:
- **Your role's estimate:** light | medium | heavy + one-line rationale.
- If you are **atlas-ai-eng** as aggregator: also return **aggregate Predicted** (max of participating roles, bumped if parallel premium gates) and a markdown table `- role: estimate (note)` for lead to paste into `budget.md` under `## Estimates by role`.

## AI artifact
The AI deliverable or the cost estimate. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/ai-eng.md`.

## References
- https://www.nist.gov/itl/ai-risk-management-framework
