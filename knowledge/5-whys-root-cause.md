---
name: 5-whys-root-cause
load-when: Investigating incidents, finding root causes, post-incident analysis
skip-when: Threat modeling (see stride-threat-modeling), risk assessment (see risk-based-testing)
---

# 5 Whys Root Cause Analysis

## Quick Reference
- Ask "why" iteratively (typically 5 times) to drill from symptom to root cause
- Stop when you reach a process or system failure, not a human error
- Each "why" should have evidence, not guesses
- Document the chain for post-incident reports
- Fix the root cause, not just the symptom

## Deep Dive

### How It Works
```
Problem: The website is down.
1. Why? → The server ran out of memory.
2. Why? → A memory leak in the application.
3. Why? → The connection pool wasn't releasing connections.
4. Why? → The code didn't handle timeout exceptions.
5. Why? → No code review checklist for resource management.
```

Root cause: missing code review checklist for resource management.

### Rules
- **Stop at process/system failures**: don't blame individuals
- **One chain per symptom**: don't mix multiple problems
- **Evidence-based**: each answer should be verifiable
- **5 is a guideline**: may need more or fewer iterations

### When to Use
- Production incidents
- Quality defects
- Process failures
- Safety incidents
- Customer complaints

### When NOT to Use
- When the cause is already obvious
- When the problem is too complex for simple causal chains
- When you need quantitative analysis (use fishbone diagram instead)

### Complementary Tools
- **Fishbone diagram**: visualize multiple cause categories
- **Fault tree analysis**: complex failure mode analysis
- **Pareto analysis**: identify the 20% of causes creating 80% of problems

### Post-Incident Template
```markdown
## Root Cause Analysis
Problem: [symptom]
1. Why? → [immediate cause]
2. Why? → [contributing factor]
3. Why? → [systemic cause]
4. Why? → [process failure]
5. Why? → [root cause]

Root cause: [summary]
Fix: [action items targeting root cause]
```

## See Also
- **stride-threat-modeling** — Threat identification
- **risk-based-testing** — Risk assessment
- **itil-incident-management** — Incident response process
- **anti-patterns** — Common failure patterns
