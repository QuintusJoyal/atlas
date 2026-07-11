---
name: model-cards
load-when: Documenting AI models, evaluating model performance, reporting bias
skip-when: AI risk management (see nist-ai-rmf), security (see owasp-llm-top-10)
---

# Model Cards

## Quick Reference
- Standardized documentation for ML models
- Includes: model details, intended use, metrics, ethical considerations
- Helps with reproducibility, accountability, and transparency
- Used for model governance and compliance
- Format: structured markdown with consistent sections

## Deep Dive

### Model Card Structure
```markdown
# Model Card: [Model Name]

## Model Details
- Developer: ...
- Version: ...
- Type: ...
- Training data: ...
- Date: ...

## Intended Use
- Primary use case: ...
- Intended users: ...
- Out-of-scope uses: ...

## Training Data
- Dataset: ...
- Size: ...
- Preprocessing: ...
- Known biases: ...

## Evaluation Data
- Dataset: ...
- Size: ...
- Metrics: ...

## Metrics
| Metric | Value | Notes |
|--------|-------|-------|
| Accuracy | ... | ... |
| Precision | ... | ... |
| Recall | ... | ... |
| F1 | ... | ... |

## Ethical Considerations
- Bias analysis: ...
- Fairness assessment: ...
- Limitations: ...

## Caveats and Recommendations
- ...
```

### Key Sections
- **Intended Use**: prevents misuse
- **Metrics**: objective performance evaluation
- **Ethical Considerations**: bias, fairness, limitations
- **Caveats**: known failure modes

### When to Create Model Cards
- Before deploying any ML model
- When sharing models with stakeholders
- For compliance and audit purposes
- When updating model versions

## See Also
- **nist-ai-rmf** — AI risk management framework
- **owasp-llm-top-10** — LLM security risks
- **anthropic-context-engineering** — Context management
- **crisp-dm** — Data science methodology
