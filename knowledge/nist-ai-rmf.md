---
name: nist-ai-rmf
load-when: Managing AI risks, evaluating AI systems, responsible AI governance
skip-when: LLM-specific risks (see owasp-llm-top-10), model documentation (see model-cards)
---

# NIST AI Risk Management Framework

## Quick Reference
- 4 functions: Govern, Map, Measure, Manage
- Applicable to all AI systems, including ML and LLMs
- Risk categories: validity, reliability, safety, security, fairness, transparency, accountability
- AI RMF Playbooks provide implementation guidance
- Maps to OECD AI Principles and ISO/IEC 23894

## Deep Dive

### Functions
| Function | Purpose | Key Activities |
|----------|---------|----------------|
| Govern | Establish AI risk management culture | Policies, roles, accountability |
| Map | Contextualize AI system risks | Impact assessment, stakeholder identification |
| Measure | Quantify and assess risks | Testing, monitoring, documentation |
| Manage | Treat and respond to risks | Mitigation, incident response, continuous improvement |

### AI Risk Categories
- **Validity and Reliability**: does the system work as intended?
- **Safety**: does it cause harm?
- **Security**: is it vulnerable to attacks?
- **Fairness**: does it produce biased outcomes?
- **Transparency**: can stakeholders understand it?
- **Accountability**: who is responsible for outcomes?

### AI RMF Profiles
- **Conversational AI Profile**: LLM-specific risks and mitigations
- **Generative AI Profile**: content generation risks
- **Context-specific Profiles**: tailored to use case

### Implementation
1. Define AI use case and context
2. Map risks using AI RMF
3. Measure risk levels
4. Manage risks with appropriate controls
5. Monitor and update continuously

## See Also
- **owasp-llm-top-10** — LLM-specific vulnerabilities
- **model-cards** — AI model documentation
- **anthropic-context-engineering** — Context management for AI
- **nist-csf** — Broader cybersecurity framework
