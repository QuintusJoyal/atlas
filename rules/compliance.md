---
name: compliance
description: Compliance and regulatory guardrails: audit procedures, evidence collection, regulatory frameworks. Load when compliance or regulatory tasks are in motion.
load: on-demand
---

# Compliance

Regulatory requirements are non-negotiable. Build compliance in, bolt it on last.

## Frameworks
- Know which frameworks apply: GDPR, SOC 2, ISO 27001, HIPAA, PCI DSS, NIST CSF.
- Reference: `k/gdpr-requirements.md`, `k/soc2-controls.md`, `k/iso-27001-annex-a.md`, `k/nist-csf.md`.
- Document which frameworks apply to the project and which controls are in scope.

## Evidence collection
- Compliance requires evidence, not assertions. Collect: configurations, access logs, scan results, approvals.
- Store evidence in an audit-ready location with timestamps.
- Automate evidence collection where possible (CI/CD pipeline artifacts, config snapshots).

## Audit preparation
- Map controls to evidence before the audit. Gaps should be identified and addressed proactively.
- Conduct internal reviews periodically, not just before external audits.
- Document exceptions and compensating controls for any gaps.

## Change management
- Compliance-relevant changes require documented approval before implementation.
- Track changes that affect compliance scope: new data stores, new access patterns, new integrations.
- Reference: `k/raid-log-management.md` for risk tracking.

## Data protection
- Data protection impact assessments (DPIAs) required before processing personal data at scale.
- Document legal basis for data processing. Reference: `k/gdpr-requirements.md`.
- Right to erasure: implement data deletion capabilities where required.

## Continuous compliance
- Compliance is ongoing, not a one-time event. Monitor controls continuously.
- Alert on control drift: configuration changes that violate policies.
- Remediate findings within defined SLAs based on severity.
