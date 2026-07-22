<!-- GENERATED FILE. Do not edit directly.
     Source: skills/atlas-security-playbook/SKILL.md (the <!-- lite:start --> block).
     Regenerate with: python3 scripts/build-lite.py -->

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
