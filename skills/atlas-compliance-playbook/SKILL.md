---
name: atlas-compliance-playbook
description: Compliance playbook for atlas-compliance.
type: playbook
appliesTo: [atlas-compliance]
tags: [playbook, compliance, gdpr, soc2, iso27001]
---

# atlas-compliance

## Route
- GDPR compliance → compliance
- SOC 2 preparation → compliance
- ISO 27001 implementation → compliance
- NIST CSF assessment → compliance
- data governance → compliance
- audit preparation → compliance

## Knowledge
- GDPR requirements → k/gdpr-requirements
- SOC 2 controls → k/soc2-controls
- ISO 27001 Annex A → k/iso-27001-annex-a
- NIST CSF → k/nist-csf
- NIST SP 800-53 → k/nist-800-53-controls

## Scope
compliance assessment, control mapping, audit preparation, data governance, privacy review | NOT technical security (→ security), implementation (→ dev), architecture (→ architect), testing (→ qa)

## Delegation Examples
### SOC 2 preparation
"Prepare for SOC 2 audit." → compliance + security in parallel: compliance maps controls to Trust Services Criteria, security validates technical controls.

### EU acquisition
"Acquired EU company, need to handle their data." → compliance: assess GDPR applicability, map data transfer mechanisms, compliance roadmap with immediate + 90-day plan.
