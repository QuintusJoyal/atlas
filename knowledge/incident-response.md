---
name: toc of contents for incident response
description: Incident response structure, runbooks, postmortems, blameless culture. Load when handling production incidents or postmortems.
load-when: task mentions incident, production issue, outage, postmortem, or on-call
skip-when: task is about new development, design, or non-production work
---

# Incident response

Incidents are inevitable. How you respond determines whether they become crises.

## Quick Reference

Incident Command System (ICS) structure: Incident Commander (overall coordination), Operations (tactical response), Planning (information gathering, root cause analysis), Logistics (resources, tools).

Severity levels: SEV1 (complete outage, data loss risk), SEV2 (degraded service, major feature broken), SEV3 (minor issue, workaround available). Response intensity scales with severity.

Postmortem: blameless, focused on systems and processes, not individuals. Root cause analysis (5 Whys, fishbone diagram). Action items with owners and deadlines.

Runbook: step-by-step guide for known failure modes. Created during calm, used during storms. Review after every incident.

## Deep Dive

### Incident response phases

**1. Detection and triage**
- Alert fires or user reports issue.
- On-call engineer acknowledges within SLA (5 min for SEV1, 15 min for SEV2).
- Initial assessment: scope, impact, severity.
- Declare incident if impact is real and unplanned.

**2. Mobilization**
- SEV1: page Incident Commander, assemble war room.
- SEV2: on-call engineer leads, page specialist if needed.
- SEV3: on-call engineer handles, escalate if needed.

**3. Containment**
- Stop the bleeding. Roll back recent changes. Disable broken feature.
- Preserve evidence (logs, metrics, traces). Don't delete or overwrite.
- Communicate status to stakeholders.

**4. Eradication and recovery**
- Identify root cause. Apply fix. Verify fix works.
- Monitor for recurrence. Confirm service is healthy.

**5. Postmortem**
- Schedule within 48 hours of incident resolution.
- Blameless: focus on "what happened" and "why," not "who."
- Root cause analysis: 5 Whys or fishbone diagram.
- Action items: specific, assigned, deadline-bound.

### Runbooks
- Create runbooks for known failure modes.
- Include: symptoms, diagnosis steps, fix steps, verification steps, escalation path.
- Test runbooks during drills. A runbook that doesn't work is worse than no runbook.
- Review and update runbooks after every incident.

### Blameless culture
- "What" and "how," not "who." Systems produce failures, not people.
- Assume everyone acted with the information they had at the time.
- Focus on preventing recurrence, not assigning blame.
- Psychological safety: people must feel safe reporting incidents and mistakes.

### Communication
- Status page for external communication.
- Internal updates every 15-30 minutes during SEV1.
- One point of communication (Incident Commander or delegate).
- After incident: transparent postmortem shared with stakeholders.

## See Also
- `k/google-sre-practices.md` for SRE practices and error budgets
- `k/itil-incident-management.md` for ITIL incident management
- `k/raid-log-management.md` for risk and issue tracking
