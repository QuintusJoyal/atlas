---
name: atlas-ai-eng-playbook
description: AI engineering playbook for atlas-ai-eng.
type: playbook
appliesTo: [atlas-ai-eng]
tags: [playbook, ai-eng, rag, agents, guardrails]
---

# atlas-ai-eng

## Route
- RAG pipeline design → ai-eng
- LLM agent design → ai-eng
- AI evaluation, guardrails → ai-eng
- team optimization, efficiency → ai-eng
- cost estimation (huddle) → ai-eng

## Knowledge
- NIST AI RMF → k/nist-ai-rmf
- OWASP LLM Top 10 → k/owasp-llm-top-10
- Anthropic context engineering → k/anthropic-context-engineering
- Model cards → k/model-cards

## Scope
RAG design, agent design, evaluation, guardrails, team optimization, cost estimation | NOT data pipelines (→ data-eng), ML models (→ data-sci), application code (→ dev), cloud architecture (→ cloud)

## Delegation Examples
### AI search feature
"Add AI search to product." → ai-eng + architect in parallel: ai-eng designs RAG pipeline, architect defines integration boundary/system constraints.

### Team optimization
"Optimize the team." → ai-eng: review usage-insights.md, identify top 3 bottlenecks/rework patterns, present prioritized improvement list.
