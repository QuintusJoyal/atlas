---
name: owasp-llm-top-10
load-when: Securing LLM applications, prompt injection defense, AI security review
skip-when: General AI risks (see nist-ai-rmf), model documentation (see model-cards)
---

# OWASP LLM Top 10

## Quick Reference
- LLM01: Prompt Injection
- LLM02: Insecure Output Handling
- LLM03: Training Data Poisoning
- LLM04: Model Denial of Service
- LLM05: Supply Chain Vulnerabilities
- LLM06: Sensitive Information Disclosure
- LLM07: Insecure Plugin Design
- LLM08: Excessive Agency
- LLM09: Overreliance
- LLM10: Model Theft

## Deep Dive

### LLM01: Prompt Injection
- Direct: user input overrides system instructions
- Indirect: malicious content in retrieved data
- Mitigation: input validation, output filtering, privilege separation

### LLM02: Insecure Output Handling
- LLM output used without sanitization
- Can lead to XSS, SSRF, command injection
- Mitigation: treat LLM output as untrusted, validate before use

### LLM06: Sensitive Information Disclosure
- LLM reveals training data, PII, or secrets
- Mitigation: data anonymization, output filtering, access controls

### LLM08: Excessive Agency
- LLM has too many permissions or capabilities
- Mitigation: least privilege, human-in-the-loop for critical actions

### LLM09: Overreliance
- Trusting LLM output without verification
- Mitigation: human review, fact-checking, confidence scoring

### Defense Patterns
- Input sanitization and validation
- Output filtering and encoding
- Rate limiting and cost controls
- Monitoring and logging
- Human-in-the-loop for critical decisions
- Sandboxing and privilege separation

## See Also
- **nist-ai-rmf** — AI risk management framework
- **owasp-top-10** — General web vulnerabilities
- **anthropic-context-engineering** — Secure context management
- **model-cards** — Model documentation
