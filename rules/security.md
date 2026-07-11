---
name: security
description: Security guardrails for threat modeling, hardening, access control, and vulnerability management. Load when a security-sensitive task is in motion.
load: on-demand
---

# Security

Applies to authentication, authorization, secrets, network, and data protection. Security is not optional.

## Threat modeling
- Before implementing any security control: (1) document the threat, (2) confirm the control addresses that specific threat, (3) verify the control does not break existing functionality.
- Use STRIDE for systematic threat classification: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege.
- Reference: `k/stride-threat-modeling.md`.

## Secrets and credentials
- Never hardcode secrets, tokens, or credentials. Read from environment variables or a secrets manager.
- Rotate secrets on a schedule. Never reuse credentials across environments.
- Use short-lived tokens where possible (JWT with expiry, ephemeral AWS credentials).

## Access control
- Apply principle of least privilege. Grant minimum permissions needed for the task.
- Separate duties: no single role should hold both creation and approval authority.
- Audit access changes. Log who granted what, when, and why.

## Input validation
- Validate and sanitize all external input at the boundary. Never trust client-side validation alone.
- Use parameterized queries. Never concatenate user input into SQL or shell commands.
- Apply allowlists over denylists where feasible.

## Vulnerability management
- Run security scans (SAST, DAST, dependency audit) before delivery.
- Triage findings: critical/high must be fixed before merge. Medium/low tracked in issue tracker.
- Reference: `k/owasp-top-10.md`, `k/owasp-asvs.md`, `k/cwe-sans-top-25.md`.

## Incident response
- If a security incident is detected during work, stop and notify the user immediately.
- Do not attempt to contain a live breach unless explicitly authorized.
- Reference: `k/incident-response.md`.
