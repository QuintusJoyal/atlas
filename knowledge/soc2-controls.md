---
name: soc2-controls
load-when: Implementing SOC 2 controls, security audits, vendor assessments
skip-when: Other compliance (see gdpr-requirements, iso-27001-annex-a), security controls (see nist-800-53-controls)
---

# SOC 2 Controls

## Quick Reference
- 5 Trust Service Criteria: Security, Availability, Processing Integrity, Confidentiality, Privacy
- Security is required; others are selected based on scope
- Type I: controls design at a point in time
- Type II: controls operating over a period (6-12 months)
- Evidence collection is ongoing

## Deep Dive

### Trust Service Criteria
| Criteria | Description | When Required |
|----------|-------------|---------------|
| Security (Common Criteria) | Protect against unauthorized access | Always |
| Availability | System operational and accessible | If availability is in scope |
| Processing Integrity | System processing is complete and accurate | If processing matters |
| Confidentiality | Protect confidential information | If confidential data exists |
| Privacy | Collect/use/retain/dispose of personal data | If personal data is processed |

### Common Criteria (CC)
- CC1: Control Environment (tone at top, ethics)
- CC2: Communication and Information
- CC3: Risk Assessment
- CC4: Monitoring Activities
- CC5: Control Activities
- CC6: Logical and Physical Access Controls
- CC7: System Operations
- CC8: Change Management
- CC9: Risk Mitigation

### Evidence Types
- Policies and procedures
- Access control lists and reviews
- Change management logs
- Incident response records
- Monitoring dashboards and alerts
- Training completion records

### Audit Process
1. scoping (which systems, criteria)
2. Readiness assessment (gap analysis)
3. Type I audit (design effectiveness)
4. Remediation
5. Type II audit (operating effectiveness)
6. Report issued

## See Also
- **gdpr-requirements** — Privacy-specific requirements
- **iso-27001-annex-a** — ISMS controls
- **nist-800-53-controls** — Security control families
- **cis-benchmarks** — Security configuration baselines
