---
name: owasp-top-10
load-when: Quick security review, vulnerability assessment, security acceptance criteria
skip-when: Detailed security controls (see owasp-asvs), threat modeling (see stride-threat-modeling)
---

# OWASP Top 10

## Quick Reference
- A01: Broken Access Control — users acting outside intended permissions
- A02: Cryptographic Failures — sensitive data exposure
- A03: Injection — untrusted data sent to interpreters
- A04: Insecure Design — missing security architecture
- A05: Security Misconfiguration — default/incomplete configs
- A06: Vulnerable Components — outdated libraries
- A07: Authentication Failures — broken identity verification
- A08: Data Integrity Failures — untrusted deserialization
- A09: Logging Failures — insufficient monitoring
- A10: SSRF — server-side request forgery

## Deep Dive

### A01: Broken Access Control
Prevent: enforce ownership, deny by default, rate limit API access, validate JWT tokens.
Example: user accesses /api/users/123/admin by changing URL to /api/users/456/admin.

### A02: Cryptographic Failures
Prevent: encrypt sensitive data at rest and in transit, use strong algorithms (AES-256, RSA-2048+), never store passwords in plaintext.
Example: credit card numbers stored unencrypted in database.

### A03: Injection
Prevent: use parameterized queries, validate/encode input, use ORMs.
Example: SQL injection via `username' OR '1'='1`.

### A04: Insecure Design
Prevent: threat modeling during design, use secure design patterns, implement defense in depth.
Example: no rate limiting on login endpoint, allowing brute force.

### A05: Security Misconfiguration
Prevent: harden defaults, remove unnecessary features, review configs regularly.
Example: debug mode enabled in production, default admin credentials.

### A06: Vulnerable Components
Prevent: inventory dependencies, use SCA tools, update regularly.
Example: using a library with known CVE.

### A07: Authentication Failures
Prevent: implement MFA, limit failed attempts, use secure session management.
Example: no account lockout after 100 failed login attempts.

### A08: Data Integrity Failures
Prevent: validate digital signatures, use trusted deserialization.
Example: deserializing untrusted data from user input.

### A09: Logging Failures
Prevent: log security events, protect log integrity, set up alerting.
Example: failed login attempts not logged.

### A10: SSRF
Prevent: validate and sanitize URLs, use allowlists for outbound requests.
Example: fetching user-supplied URL that points to internal services.

## See Also
- **owasp-asvs** — Detailed security verification controls
- **stride-threat-modeling** — Threat identification methodology
- **nist-800-53-controls** — Security control families
- **cwe-sans-top-25** — Most dangerous software weaknesses
