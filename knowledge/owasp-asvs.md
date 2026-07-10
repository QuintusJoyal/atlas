---
name: owasp-asvs
load-when: Reviewing security controls, verifying application security, designing security requirements
skip-when: Threat modeling (see stride-threat-modeling), vulnerability scanning (see owasp-top-10)
---

# OWASP ASVS

## Quick Reference
- ASVS = Application Security Verification Standard
- Three assurance levels: L1 (minimum), L2 (standard), L3 (high)
- Covers: architecture, authentication, authorization, validation, cryptography, error handling, logging, data protection, communication, business logic
- Use to define security acceptance criteria for features
- Maps to OWASP Top 10 and NIST SP 800-53

## Deep Dive

### What ASVS Provides
A standard framework for verifying application security. Unlike the Top 10 (which lists vulnerabilities), ASVS defines what security controls should exist and how to verify them.

### Assurance Levels
| Level | Description | When to Use |
|-------|-------------|-------------|
| L1 | Minimum | Apps handling low-sensitivity data |
| L2 | Standard | Most web applications, APIs, microservices |
| L3 | High | Financial, healthcare, critical infrastructure |

### ASVS Control Categories (v5.0)
1. **Architecture**: threat modeling, security design patterns, access control architecture
2. **Authentication**: credential management, session management, MFA
3. **Authorization**: access control, permission models, RBAC/ABAC
4. **Input validation**: injection prevention, sanitization, encoding
5. **Cryptography**: key management, encryption at rest/transit, hashing
6. **Error handling**: error messages, logging, stack traces
7. **Logging**: audit trails, log integrity, monitoring
8. **Data protection**: sensitive data handling, encryption, masking
9. **Communication**: TLS, certificate validation, secure protocols
10. **Business logic**: abuse cases, rate limiting, anti-automation

### Using ASVS in Development
1. Select assurance level (L1/L2/L3) based on data sensitivity
2. Map ASVS requirements to feature acceptance criteria
3. Verify controls during code review and security testing
4. Document verification results

### ASVS and Other Standards
- OWASP Top 10: ASVS provides detailed controls for Top 10 risks
- NIST SP 800-53: ASVS maps to many NIST controls
- PCI DSS: ASVS can be used to verify PCI requirements
- SOC 2: ASVS controls support SOC 2 trust criteria

## See Also
- **owasp-top-10** — Quick list of top web vulnerabilities
- **stride-threat-modeling** — Threat identification methodology
- **nist-800-53-controls** — Security control families
- **soc2-controls** — Trust service criteria
- **iso-27001-annex-a** — ISMS controls
