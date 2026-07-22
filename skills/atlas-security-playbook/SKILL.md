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

## Lite mode

Generated into `lite/skills/atlas-security-playbook/SKILL.md` by `scripts/build-lite.py`. Edit the block below, then run the script — never hand-edit the `lite/` output directly.

<!-- lite:start -->
# atlas-security (Lite Playbook)

## Route
- security review → atlas-security
- threat modeling → atlas-security
- vulnerability scan → atlas-security
- security hardening → atlas-security

## Rules
1. Threat model before implementing controls.
2. Apply least privilege. Never hardcode secrets.
3. Run scans before delivery. Fix critical/high findings.

## Knowledge (inlined, no external files)
- OWASP Top 10: A01 Broken Access Control, A02 Cryptographic Failures, A03 Injection, A04 Insecure Design, A05 Security Misconfiguration, A06 Vulnerable Components, A07 Authentication Failures, A08 Data Integrity Failures, A09 Logging Failures, A10 SSRF.
- OWASP ASVS: verification levels L1 (minimum) / L2 (standard) / L3 (high). Defines what controls should exist and how to verify them, not just what's vulnerable.
- STRIDE: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. Check every system component against all 6.
<!-- lite:end -->
