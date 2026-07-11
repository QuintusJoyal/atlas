---
name: gdpr-requirements
load-when: Handling personal data, implementing data subject rights, privacy reviews
skip-when: Other compliance frameworks (see soc2-controls, iso-27001-annex-a), data warehousing (see kimball-dimensional-modeling)
---

# GDPR Requirements

## Quick Reference
- Applies to any org processing EU residents' personal data
- Lawful basis required: consent, contract, legal obligation, vital interests, public task, legitimate interests
- Data subject rights: access, rectification, erasure, portability, restriction, objection
- 72-hour breach notification requirement
- Data Protection Impact Assessment (DPIA) for high-risk processing

## Deep Dive

### Lawful Basis for Processing
| Basis | Description | Example |
|-------|-------------|---------|
| Consent | Clear, specific, informed agreement | Marketing emails |
| Contract | Necessary for contract performance | Order processing |
| Legal Obligation | Required by law | Tax records |
| Vital Interests | Protect someone's life | Emergency medical data |
| Public Task | Official authority | Public records |
| Legitimate Interests | Business need, balanced against rights | Fraud prevention |

### Data Subject Rights
1. **Right of Access**: know what data is held
2. **Right to Rectification**: correct inaccurate data
3. **Right to Erasure**: delete personal data
4. **Right to Portability**: receive data in machine-readable format
5. **Right to Restriction**: limit processing
6. **Right to Object**: stop processing
7. **Rights re: Automated Decision Making**: human review of automated decisions

### Data Protection Principles
1. Lawfulness, fairness, transparency
2. Purpose limitation
3. Data minimization
4. Accuracy
5. Storage limitation
6. Integrity and confidentiality (security)
7. Accountability

### Breach Notification
- Supervisory authority: within 72 hours
- Data subjects: without undue delay (if high risk)
- Document: what happened, impact, remediation

### DPIA Process
1. Identify need for DPIA
2. Describe processing
3. Assess necessity and proportionality
4. Identify and assess risks
5. Identify measures to mitigate risks
6. Consult with DPO and stakeholders

## See Also
- **soc2-controls** — Trust service criteria
- **iso-27001-annex-a** — ISMS controls
- **nist-csf** — Cybersecurity framework
- **compliance-anti-patterns** — Common privacy failures
