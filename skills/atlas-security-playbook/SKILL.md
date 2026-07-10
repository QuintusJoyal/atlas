---
name: atlas-security-playbook
description: Security playbook for atlas-security.
type: playbook
appliesTo: [atlas-security]
tags: [playbook, security, owasp, stride]
---

# atlas-security

## Route
- security review, threat modeling → security
- OWASP checks → security
- secrets scanning → security
- vulnerability assessment → security
- security architecture → security

## Knowledge
- OWASP ASVS v5.0 → k/owasp-asvs
- OWASP Top 10 (2021) → k/owasp-top-10
- STRIDE threat modeling → k/stride-threat-modeling
- NIST SP 800-53 → k/nist-800-53-controls
- CWE/SANS Top 25 → k/cwe-sans-top-25
- GDPR requirements → k/gdpr-requirements

## Scope
security review, threat modeling, OWASP checks, secrets scanning, vulnerability assessment, security architecture recommendations | NOT implementation (→ dev), testing (→ qa), compliance audit (→ compliance), deployment (→ devops)

## Delegation Examples
### Pre-deploy security gate
"Release ready for security review." → security: scan diff for secrets, verify threat model updated, SAST on changed files, pass/block verdict.

### API endpoint security
"New endpoint handles PII." → security: audit auth/data handling, verify rate limiting, check TLS config. Findings with severity + concrete fixes.

### Dependency vulnerability
"CVE disclosed in dependency." → security: assess exploitability in our context, true/false positive determination, emergency triage report with patch recommendation.
