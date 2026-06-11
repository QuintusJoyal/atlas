# Workflow: security-audit

Read-only assessment. No code changes.

## Phases and roles
1. Scope: atlas-pm or atlas-consultant confirms targets and threat model with the user
2. Audit: atlas-security (OWASP, STRIDE, secrets)
3. Review: atlas-reviewer (quality and charter conformance)
4. Compliance: atlas-compliance (regulatory and governance)
5. Report: atlas-docs assembles findings
6. Gate: final delivery (user) reviews the report and decides on remediation

## Default tiers
Premium: atlas-security, atlas-reviewer, atlas-compliance. Fast: atlas-docs.

## Definition of Done
- Findings by severity with concrete remediation.
- Compliance gaps mapped to frameworks.
- Clear, prioritized report for the user. No changes applied.
