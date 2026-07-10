---
name: atlas-security-playbook
description: Security methodology for atlas-security: OWASP checks, STRIDE threat modeling, and secrets scanning. Use when atlas-security runs.
disable-model-invocation: true
---

# Security engineer playbook

Standards: OWASP ASVS and OWASP Top 10, NIST SSDF, STRIDE threat modeling. Read only: recommend fixes, do not apply them.

## OWASP Top 10 quick checks
Injection, broken access control, cryptographic failures, insecure design, security misconfiguration, vulnerable dependencies, auth failures, integrity failures, logging gaps, SSRF.

## STRIDE threat model
Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. For each asset and entry point, list threats and mitigations.

## Secrets scan
Check for hardcoded secrets, tokens, and keys in code, config, and history. Confirm secrets come from environment or a manager.

## Input and authz
Validate and sanitize all external input. Verify authorization on every sensitive path.

## Security artifact
Findings by severity (Critical, High, Medium), each with a concrete fix, plus a pass or block recommendation. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/security.md`.

## References
- https://owasp.org/www-project-application-security-verification-standard/
- https://owasp.org/www-project-top-ten/
- https://csrc.nist.gov/publications/detail/sp/800-218/final
