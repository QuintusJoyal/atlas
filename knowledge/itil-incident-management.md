---
name: itil-incident-management
load-when: Handling production incidents, defining escalation paths, managing service disruptions
skip-when: SRE practices (see google-sre-practices), deployment (see gitops-principles)
---

# ITIL Incident Management

## Quick Reference
- Incident: unplanned interruption or degradation of service
- Goal: restore normal service as quickly as possible
- Severity: impact × urgency
- Major incident: significant business impact, requires dedicated team
- Communication: keep stakeholders informed throughout

## Deep Dive

### Incident Lifecycle
1. **Detection**: automated alerts or user reports
2. **Triage**: assess severity and impact
3. **Categorization**: classify incident type
4. **Prioritization**: severity determines response time
5. **Investigation**: diagnose root cause
6. **Resolution**: fix the issue
7. **Recovery**: restore service
8. **Closure**: document and close

### Severity Levels
| Severity | Impact | Response Time | Update Frequency |
|----------|--------|---------------|------------------|
| P1 Critical | Service down, major users affected | 15 minutes | Every 30 minutes |
| P2 High | Service degraded, significant impact | 1 hour | Every 2 hours |
| P3 Medium | Service impaired, limited impact | 4 hours | Daily |
| P4 Low | Minor issue, workaround available | 24 hours | As needed |

### Major Incident Process
1. Declare major incident (P1/P2)
2. Assemble incident team (IC + subject matter experts)
3. Set up war room (virtual or physical)
4. Assign roles: IC, communicator, scribe
5. Diagnose and resolve
6. Post-incident review (blameless)

### Communication Templates
**Initial notification:**
"We are investigating [symptom]. Impact: [description]. Next update: [time]."

**Update:**
"Status: [investigating/identified/monitoring]. Impact: [description]. ETA: [time or 'TBD']."

**Resolution:**
"Service has been restored. Root cause: [brief]. Full postmortem to follow."

### Escalation
- **Functional escalation**: bring in subject matter experts
- **Hierarchical escalation**: inform management when business impact is significant
- **Automatic escalation**: if response time SLA is breached

## See Also
- **google-sre-practices** — SRE approach to incident response
- **dora-metrics** — Measuring incident response effectiveness
- **anti-patterns** — Common incident management failures
- **raid-log-management** — Tracking risks and issues
