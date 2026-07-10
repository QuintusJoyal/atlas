---
name: atlas-compliance-playbook
description: Compliance methodology for atlas-compliance: GDPR, SOC 2, ISO 27001, NIST CSF, and data governance. Use when atlas-compliance runs.
disable-model-invocation: true
---

# Compliance, GRC, and privacy playbook

Standards: GDPR, SOC 2, ISO 27001, NIST CSF, DAMA-DMBOK data governance, privacy by design. Read only: assess and recommend.

## Scope the obligations
Identify which frameworks and data types apply (personal data, regulated data, customer commitments). Do not assume; confirm with the user.

## Assess
- Privacy by design: data minimization, purpose limitation, consent, retention, subject rights.
- Controls: access, encryption, logging, change management, vendor risk.
- Map controls to the applicable framework and note gaps.

## Boundary with security
atlas-security covers technical vulnerabilities. You cover regulatory and governance obligations. Coordinate on overlaps.

## Compliance artifact
Findings, required controls, gaps, and a pass or block recommendation. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/compliance.md`.

## References
- https://gdpr.eu/
- https://www.aicpa.org/soc
- https://www.iso.org/standard/54534.html
- https://www.nist.gov/cyberframework
