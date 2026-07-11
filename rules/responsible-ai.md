---
name: responsible-ai
description: Responsible AI guardrails: bias detection, model risk, transparency, human oversight. Load when AI/ML work is in motion.
load: on-demand
globs: "**/*.{py,ipynb,yaml,yml,json}"
---

# Responsible AI

AI systems affect people. Build them with care, transparency, and accountability.

## Bias and fairness
- Test models for demographic bias before deployment. Measure performance across subgroups.
- Use fairness metrics (demographic parity, equalized odds) appropriate to the domain.
- Document known limitations and affected populations in the model card.
- Reference: `k/model-cards.md`, `k/nist-ai-rmf.md`.

## Transparency
- Document model purpose, training data sources, evaluation metrics, and known limitations.
- Provide explainability for high-stakes decisions (feature importance, SHAP values, or equivalent).
- Publish model cards for all production models. Reference: `k/model-cards.md`.

## Human oversight
- High-stakes AI decisions (credit, hiring, healthcare, legal) require human review before action.
- Implement confidence thresholds: below threshold, route to human review.
- Never fully automate irreversible decisions without human confirmation.

## Safety
- Run adversarial testing (red-teaming) before deployment.
- Reference: `k/owasp-llm-top-10.md` for LLM-specific risks.
- Monitor for prompt injection, data exfiltration, and unintended behavior in production.

## Data governance
- Training data must comply with data governance rules. See `rules/data-governance.md`.
- Document data provenance: source, licensing, consent, and known gaps.
- Do not train on data without proper authorization.

## Continuous monitoring
- Monitor model performance and drift in production.
- Set alerting thresholds for accuracy, latency, and fairness metrics.
- Retrain or retire models that degrade beyond acceptable bounds.
