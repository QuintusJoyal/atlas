---
name: atlas-data-sci-playbook
description: Data science playbook for atlas-data-sci.
type: playbook
appliesTo: [atlas-data-sci]
tags: [playbook, data-sci, ml, crisp-dm]
---

# atlas-data-sci

## Route
- ML model development → data-sci
- model evaluation → data-sci
- feature engineering → data-sci
- bias/fairness assessment → data-sci
- CRISP-DM methodology → data-sci

## Knowledge
- CRISP-DM methodology → k/crisp-dm
- NIST AI RMF → k/nist-ai-rmf
- Model cards → k/model-cards
- OWASP LLM Top 10 → k/owasp-llm-top-10

## Scope
ML model development, evaluation, feature engineering, bias/fairness, CRISP-DM | NOT data pipelines (→ data-eng), analytics (→ data-analyst), LLM agent design (→ ai-eng), data warehouse (→ dba)

## Delegation Examples
### Recommendation engine
"Build real-time recommendations." → data-sci + data-eng in parallel: feature engineering pipeline + model development are co-dependent.

### Privacy-sensitive model
"Model trained on potentially sensitive data." → data-sci: assess data provenance, check PII leakage in features, recommend privacy-preserving alternatives, flag compliance risks.
