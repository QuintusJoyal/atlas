---
name: cis-benchmarks
load-when: Hardening systems, security configuration, compliance baseline
skip-when: Security controls (see nist-800-53-controls), threat modeling (see stride-threat-modeling)
---

# CIS Benchmarks

## Quick Reference
- CIS = Center for Internet Security
- Consensus-based security configuration baselines
- Covers: operating systems, cloud providers, applications, network devices
- Two levels: Level 1 (essential) and Level 2 (defense-in-depth)
- Use as starting point, customize for your environment

## Deep Dive

### Benchmark Structure
Each benchmark provides:
- Recommended configuration settings
- Rationale for each setting
- Impact of applying the setting
- Audit procedures
- Remediation steps

### Benchmark Categories
- **Operating Systems**: Windows, Linux, macOS
- **Cloud Providers**: AWS, Azure, GCP
- **Applications**: Docker, Kubernetes, databases
- **Network Devices**: firewalls, switches, routers

### Levels
| Level | Description | When to Use |
|-------|-------------|-------------|
| Level 1 | Essential security | All environments |
| Level 2 | Defense-in-depth | Sensitive data, high-security |
| Level 3 | Strictest controls | Regulated environments |

### Using CIS Benchmarks
1. Select relevant benchmarks
2. Assess current configuration
3. Apply Level 1 controls
4. Evaluate impact
5. Apply Level 2+ controls as needed
6. Document exceptions

### Automation
- CIS-CAT Pro: automated assessment tool
- Ansible/Chef/Puppet: automated remediation
- Integrate into CI/CD for continuous compliance

## See Also
- **nist-800-53-controls** — Security control families
- **soc2-controls** — Trust service criteria
- **iso-27001-annex-a** — ISMS controls
- **aws-well-architected** — Cloud security pillar
