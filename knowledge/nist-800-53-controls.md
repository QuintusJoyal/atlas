---
name: nist-800-53-controls
load-when: Designing security controls, compliance mapping, security architecture review
skip-when: Quick vulnerability list (see owasp-top-10), threat modeling (see stride-threat-modeling)
---

# NIST SP 800-53 Security Controls

## Quick Reference
- 20 control families: AC (Access Control), AU (Audit), CA (Assessment), CM (Config Mgmt), CP (Contingency), IA (Identity), IR (Incident), MA (Maintenance), MP (Media), PE (Physical), PL (Planning), PM (Program), PS (Personnel), PT (PII), RA (Risk), SA (System Acquisition), SC (System Comms), SI (System Integrity), SR (Supply Chain), PM (Program Management)
- Control baselines: Low, Moderate, High impact
- Tailor controls to project needs
- Maps to OWASP ASVS, SOC 2, ISO 27001

## Deep Dive

### Control Families (Most Relevant)
| Family | Name | Key Controls |
|--------|------|--------------|
| AC | Access Control | AC-2 (Account Mgmt), AC-3 (Access Enforcement), AC-6 (Least Privilege) |
| AU | Audit | AU-2 (Audit Events), AU-3 (Content), AU-6 (Review) |
| CM | Config Management | CM-2 (Baseline), CM-3 (Change Control), CM-6 (Config Settings) |
| IA | Identification & Auth | IA-2 (MFA), IA-5 (Password Mgmt), IA-8 (Non-Org Users) |
| RA | Risk Assessment | RA-3 (Risk Analysis), RA-5 (Vulnerability Scanning) |
| SC | System Comms | SC-8 (Confidentiality), SC-13 (Cryptography), SC-28 (At Rest) |
| SI | System Integrity | SI-2 (Flaw Remediation), SI-3 (Malware), SI-10 (Info Input Validation) |
| SR | Supply Chain | SR-3 (Supply Chain Controls), SR-5 (Tamper Resistance) |

### Impact Levels
- **Low**: minimal damage, limited scope
- **Moderate**: serious damage, significant scope
- **High**: severe/catastrophic damage, broad scope

### Using NIST 800-53
1. Determine impact level (FIPS 199)
2. Select control baseline
3. Tailor controls to project needs
4. Document in System Security Plan (SSP)
5. Implement and verify controls
6. Continuous monitoring

### Control Selection Process
1. Start with baseline for your impact level
2. Add controls based on specific risks
3. Remove controls that don't apply (document justification)
4. Supplement with project-specific controls

## See Also
- **owasp-asvs** — Application-specific security verification
- **owasp-top-10** — Quick vulnerability list
- **nist-csf** — Cybersecurity Framework (broader than 800-53)
- **soc2-controls** — Trust service criteria
- **iso-27001-annex-a** — ISMS controls
