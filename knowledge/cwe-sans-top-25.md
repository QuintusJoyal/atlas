---
name: cwe-sans-top-25
load-when: Prioritizing security fixes, vulnerability classification, code review focus
skip-when: Quick vulnerability list (see owasp-top-10), detailed controls (see owasp-asvs)
---

# CWE/SANS Top 25

## Quick Reference
- 25 most dangerous software weaknesses ranked by frequency and impact
- Categories: Porous Defenses, Insecure Interaction, Dangerous Resources, Poor Data Protection
- Use to prioritize code review and static analysis findings
- Maps to OWASP Top 10 and NIST SP 800-53
- Updated annually based on NVD data

## Deep Dive

### Most Critical (Rank 1-5)
| Rank | CWE | Name | Description |
|------|-----|------|-------------|
| 1 | CWE-787 | Out-of-bounds Write | Writing data beyond buffer boundaries |
| 2 | CWE-79 | XSS | Untrusted data in web page without validation |
| 3 | CWE-89 | SQL Injection | Untrusted data in SQL commands |
| 4 | CWE-416 | Use After Free | Accessing memory after it's been freed |
| 5 | CWE-78 | OS Command Injection | Untrusted data in OS commands |

### Categories
**Porous Defenses** (CWE-787, 79, 89, 78, 20, 125, 22, 352, 434, 862)
- Weaknesses that allow attackers to bypass security controls

**Insecure Interaction** (CWE-416, 787, 20)
- Weaknesses arising from how components interact

**Dangerous Resources** (CWE-416, 787, 22)
- Weaknesses related to resource management

**Poor Data Protection** (CWE-200, 284, 862)
- Weaknesses in protecting sensitive data

### Prevention Patterns
- **CWE-787**: bounds checking, safe memory functions
- **CWE-79**: output encoding, input validation, CSP headers
- **CWE-89**: parameterized queries, stored procedures, input validation
- **CWE-416**: memory-safe languages, smart pointers, RAII
- **CWE-78**: input validation, avoid OS commands, use APIs

### Using in Code Review
1. Run static analysis tools that map to CWE
2. Prioritize findings by CWE rank
3. Focus review on high-rank CWEs in critical code paths
4. Track remediation by CWE category

## See Also
- **owasp-top-10** — Web vulnerability categories
- **owasp-asvs** — Security verification controls
- **clean-code-practices** — Code quality that prevents vulnerabilities
- **nist-800-53-controls** — Security control families
